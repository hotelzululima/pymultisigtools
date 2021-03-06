#!/usr/bin/env python

import sys
import threading
import time
import io
import os
import nacl.secret
import nacl.utils
import gui
import gtk
import json
import errno
import bitcoin
from pbkdf2 import PBKDF2 
from Singleton import Singleton 
import lib

@Singleton
class Settings:


    def __init__( self, settingsFile = "settings.json.nacl" ):
        #might as well define this as a constant
        #otherwise we end up with magic numbers elsewhere
        self.PASSWORD_SALT_SIZE = 8
        self.passwordLock = threading.Lock()
        self.key = None
        self.deleteCallbackThread = None
        self.salt = None
        self.cypherText = None
        self.settingsHash = None

        if hasattr(sys,'frozen'):
            self.settingsFilePath = os.path.join( os.path.expanduser( "~" ), settingsFile )
        else:
            self.settingsFilePath = os.path.join( sys.path[0], settingsFile )
    

    def load_config_file( self ):
        settingsFile = None
        try:
            settingsFile = io.FileIO( self.settingsFilePath, 'r' )
            self.salt = settingsFile.read( self.PASSWORD_SALT_SIZE )
            self.cypherText = settingsFile.readall()
        except IOError as e:
            if( e.errno == errno.ENOENT ):
                return
            alarmDiag = gtk.MessageDialog( None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, "Cannot open configuration file" )
            alarmDiag.format_secondary_text( os.strerror( e.errno ) )
            alarmDiag.run()
            alarmDiag.destroy()
        finally:
            if settingsFile is not None:
                settingsFile.close() 

    def restore_backup_json( self, backup_json ):
        clean_settings = lib.KeyHelper.clean_settings( backup_json )

        #back this up in case something bad happens and we have to rollback
        old_salt = self.salt
        old_cypherText = self.cypherText
        old_get_settings_json = self.get_settings_json

        self.salt = None
        self.cypherText = None
        self.get_settings_json = lambda: True;

        try: 
            self.delete_key()
            new_settings_json = self.save_config_file( clean_settings )
        except Exception as e:
            self.salt = old_salt
            self.cypherText = old_cypherText
            raise e
        finally:
            self.get_settings_json = old_get_settings_json

        return clean_settings

    def save_config_file( self, newSettings ):
        self.settingsHash = newSettings
        try:
            if( self.settingsHash is None ):
                raise RuntimeError( "Invalid State", "Tried to save settings that were never set" )

            #this is just to make sure that we have a valid key
            self.get_settings_json()

            mykey = self.get_key()
            settingsString = json.dumps( self.settingsHash )
            secretBox = nacl.secret.SecretBox( mykey )
            nonce = nacl.utils.random( nacl.secret.SecretBox.NONCE_SIZE )
            self.cypherText = secretBox.encrypt( settingsString, nonce )
            settingsFile = io.FileIO( self.settingsFilePath, 'w' )
            settingsFile.write( self.salt )
            settingsFile.write( self.cypherText )
            settingsFile.close()
        finally:
            if self.passwordLock.locked():
                self.passwordLock.release()

    def get_settings_json( self ):
        if( self.cypherText is None ):
            self.load_config_file()
        if( self.cypherText is None ):
            return self.get_default_settings()
        try:
            mykey = self.get_key()
            secretBox = nacl.secret.SecretBox( mykey )
            jsonbytes = secretBox.decrypt( self.cypherText )
            configJson = jsonbytes.encode( "utf-8" )
            return json.loads( configJson, object_hook=self.fix_account_keys )
        except nacl.exceptions.CryptoError as e:
            if self.passwordLock.locked():
                self.passwordLock.release()
            self.delete_key()
            raise e
        finally:
            if self.passwordLock.locked():
                self.passwordLock.release()

    def fix_account_keys( self, indict ):
        returndict = dict()
        for key, value in indict.items():
            if key.isdigit():
                returndict[int(key)] = value
            else:
                returndict[key] = value
        return returndict

    #delete the key after it's time'd out 
    def delete_key( self ):
        self.passwordLock.acquire()
        self.key = None
        self.passwordLock.release()

    def get_default_settings( self ):
        defaults = { "bip32master": None }
        return defaults

    def cancel_callback( self ):
        if( self.deleteCallbackThread is not None ):
            self.deleteCallbackThread.cancel()

    #everything should use this function if they need the key
    #to ensure that it gets timed out correctly
    #everybody that calls this function is expected to release 
    #the password lock after it's done using the key
    def get_key( self ):
        self.passwordLock.acquire()
        self.cancel_callback()

        if( self.key is not None ):
            self.deleteCallbackThread = threading.Timer( 30.0, self.delete_key )
            self.deleteCallbackThread.start()
            return self.key

        password = None

        if self.salt is None:
            while True:
                password1 = gui.PasswordEntry.get_password_from_user( "New Password" )
                password2 = gui.PasswordEntry.get_password_from_user( "Confirm Password" )
                if password1 == password2:
                    password = password1
                    break
            self.salt = nacl.utils.random( self.PASSWORD_SALT_SIZE )
        else:
            password = gui.PasswordEntry.get_password_from_user( "Configuration Password" )
        
        self.key = PBKDF2( password, self.salt ).read( nacl.secret.SecretBox.KEY_SIZE )
        self.deleteCallbackThread = threading.Timer( 30.0, self.delete_key )
        self.deleteCallbackThread.start()
        return self.key

