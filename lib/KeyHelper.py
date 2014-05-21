#!/usr/bin/env python
import gui
import gtk
from Settings import Settings
import exceptions
import bitcoin

class KeyHelper:

    #displays a dialog to display to the user
    #about the next public key
    @staticmethod
    def show_next_public_key_dialog(*args):
        try:
            next_key = KeyHelper.get_next_public_key( )
            diag = gtk.MessageDialog( None, gtk.DIALOG_MODAL, gtk.MESSAGE_INFO, gtk.BUTTONS_OK , "Your new key:" )
            diag.format_secondary_markup( next_key )
            diag.run()
            diag.destroy()
        except Exception as e:
            diag = gtk.MessageDialog( None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK , "Cannot get new key" )
            diag.format_secondary_markup( str( e ) )
            diag.run()
            diag.destroy()
            return False

        return True

        


    @staticmethod
    def get_next_public_key(  ):
        settings = Settings.Instance().get_settings_json()

        if( settings['bip32master'] is None ):
            raise RuntimeError( "Master key has not been set up yet" )

        account_number = settings['accountNumber']
        account_info = settings['accounts'][account_number]
        account_key = account_info['accountKey']
        key_number = account_info['numKeys']

        key_number += 1

        return_key = bitcoin.bip32_ckd( account_key, key_number )
        return_key = bitcoin.bip32_extract_key( return_key )
        return_key = bitcoin.privtopub( return_key )

        #remember to save our new key
        settings['accounts'][account_number]['numKeys'] = key_number
        Settings.Instance().save_config_file( settings )

        return return_key

