import pickle
import os

class Credential:
    credentials_path = '../data/keys/'

    def __init__(self, name, s_key=None, s_password=None):
        self.name = name
        self.key_file_path = f'{self.credentials_path}{self.name}_credentials.p'
        if(s_key is None and s_password is None):
            self.import_file()
        else:
            self.session_key = s_key
            self.session_password = s_password

    def export_file(self):
        user_credentials = {
            'name': self.name,
            'session_key': self.session_key,
            'session_password': self.session_password,
        }

        if not os.path.exists(self.credentials_path):
            os.makedirs(self.credentials_path)
            print("Directory " , self.credentials_path ,  " Created ")

        with open(self.key_file_path, 'bw') as f:
            pickle.dump(user_credentials, f)
        print(f'{self.key_file_path} Created')

    def import_file(self):
        try:
            with open(self.key_file_path, 'br') as f:
                loaded_dict = pickle.load(f)
                self.name = loaded_dict['name']
                self.session_key = loaded_dict['session_key']
                self.session_password = loaded_dict['session_password']
        except FileNotFoundError as e:
            print('ERROR: No Credential file found.')
            raise(e)

    def to_dict(self): 
        return {
            'name': self.name,
            'session_key': self.session_key,
            'session_password': self.session_password
        }
    
