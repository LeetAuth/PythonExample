# Importing requests module for talking to the API
import requests
# Importing JSON for reading the response body
import json
# Importing simplejson for error handling when downloading a file
import simplejson

from urllib.parse import urlencode


class LeetAuth:
    def __init__(self, identifier: str):
        self.base_url = "https://api.leet-auth.dev/public"
        self.app_id = identifier
        self.auth_token = ""

    def url(self, path: str) -> str:
        return self.base_url + path

    @staticmethod
    def format_json(json_body: dict) -> str:
        return json.dumps(json_body, indent=4, ensure_ascii=True)

    @property
    def headers(self) -> dict:
        return {
            "Authorization": self.auth_token,
            "User-Agent": "LeetAuth"
        }

    # Pre-Auth Functions
    def login(self, username: str, password: str, **kwargs) -> str:
        response = requests.post(self.url("/authenticate"), params={
            "app": self.app_id,
            "username": username,
            "password": password,
            "hwid": kwargs.get("hwid", ""),
            "checksum": kwargs.get("checksum", "")
        }, headers=self.headers)
        # Getting the JSON response from our API
        json_body =  response.json()
        # Assigning the JWT to our session
        if json_body["status"]:
            self.auth_token = json_body["token"]
        return self.format_json(json_body)

    def register(self, username: str, password: str, license_key: str, **kwargs) -> str:
        response = requests.post(self.url("/register"), params={
            "app": self.app_id,
            "username": username,
            "password": password,
            "license": license_key,
            "hwid": kwargs.get("hwid", ""),
            "checksum": kwargs.get("checksum", "")
        }, headers=self.headers)
        return self.format_json(response.json())

    def renew_plan(self, username: str, license: str) -> str:
        response = requests.post(self.url("/renew"), params={
            "app": self.app_id,
            "username": username,
            "license": license_key,
        }, headers=self.headers)
        return self.format_json(response.json())


    # Post-Auth functions
    def get_properties(self) -> str:
        response = requests.get(self.url("/properties"), params={
            "app": self.app_id,
        }, headers=self.headers)
        return self.format_json(response.json())

    def change_password(self, new_password: str, confirm_new_password: str) -> str:
        response = requests.post(self.url("/change_password"), params={
            "app": self.app_id,
            "new_password": new_password,
            "cnf_password": confirm_new_password
        }, headers=self.headers)
        return self.format_json(response.json())

    def get_login_logs(self) -> str:
        response = requests.get(self.url("/logins"), params={
            "app": self.app_id,
        }, headers=self.headers)
        return self.format_json(response.json())

    def download_file(self, file_name: str, path_to_save: str) -> str:
        response = requests.get(self.url("/files/") + file_name, params={
            "app": self.app_id,
        }, headers=self.headers, allow_redirects=True)
        try:
            json_body = response.json()
        except simplejson.errors.JSONDecodeError:
            # Writing the file in chunks, its a better way of writing if the file is big
            with open(path_to_save, 'wb') as downloaded_file:
                for chunk in response.iter_content(chunk_size=128):
                    downloaded_file.write(chunk)
            # Returning a hardocded sucess response
            return self.format_json({
                "status": True,
                "note": "Successfully downloaded the file"
            })
        return self.format_json(json_body)

    def get_variable(self, variable_name: str) -> str:
        response = requests.get(self.url("/variables/") + variable_name, params={
            "app": self.app_id,
        }, headers=self.headers)
        return self.format_json(response.json())

auth = LeetAuth("197238084039-680135171323")
print(auth.register(USERNAME, PASSWORD, LICENSE, hwid=HWID, checksum=CHECKSUM))
print(auth.login("0xD", "testpassword123", hwid="234234234", checksum="243235fsdf"))
if auth.auth_token == "":
    print("Something went wrong during the authentication")
    # Exitting the app and returning a non 0 response
    exit(1)

print(auth.get_properties())
# Uncomment this to change the password
print(auth.change_password("newPassword123!", "newPassword123!"))
print(auth.get_login_logs())
print(auth.download_file("hey.txt", "./myfile.txt"))
print(auth.get_variable("myVariable"))
print(auth.renew_plan("username", "license-key"))
