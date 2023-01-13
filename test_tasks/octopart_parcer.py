import pandas as pd
import numpy as np
import base64
import requests
import time
import json


class OctopartParser:

    NEXAR_URL = "https://api.nexar.com/graphql"
    PROD_TOKEN_URL = "https://identity.nexar.com/connect/token"


    def __init__(self, client_id :str, client_secret :str):
        #  initialize session
        self.client_id = client_id
        self.client_secret = client_secret
        self.token = self.get_token()

        #  start session
        self.session = requests.Session()
        self.session_time = self.get_time()
        self.session.headers.update({"token": self.token.get('access_token')})



    # func to get access_token
    def get_token(self):

        try:
            token = requests.post(
                url=self.PROD_TOKEN_URL,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret
                },
                allow_redirects=False,
            ).json()

        except Exception:
            raise

        return token

    # func to capture session start time
    def get_time(self):

        decoded_token = json.loads(
            (base64.urlsafe_b64decode(self.token.get('access_token').split(".")[1] + "==")).decode("utf-8")
        ).get('exp')

        return decoded_token

    # func to check expiration time of the token-key
    def check_expiration(self):

        if self.session_time < (time.time() + 300):
            get_token(self.client_id, self.client_secret)
            self.session.headers.update({"token": self.token.get('access_token')})
            self.session_time = get_time()

    # func to perform query
    def get_query(self, query :str, variables :dict):

        try:
            self.check_expiration()
            primary_response = self.session.post(
                self.NEXAR_URL,
                json={"query": query, "variables": variables},
            )

        except Exception:
            print(Exception)
            raise Exception("Error while getting response")

        response = primary_response.json()
        if ("errors" in response):
            for error in response["errors"]: print(error["message"])
            raise SystemExit

        return response["data"]


    # func to get all octopart categories
    def get_all_categories(self, file_name :str, variables=None):

        QUERY_CATEGORIES = '''
        query Categories {
          supCategories {
            id
            name
            path
            numParts
            parentId
            children {
              id
            }
            relevantAttributes{
              id
            }
          }
        }

                    '''

        categories = self.get_query(QUERY_CATEGORIES, variables)
        categories = pd.DataFrame(categories['supCategories'])
        categories.to_csv(file_name, sep=',', encoding='utf-8')

        return categories

    # func to get all available manufacturers on octopart.com
    def get_all_manufacturers(self, file_name, variables=None):
        QUERY_MANUFACTURERS = '''
        query Manufacturers {
          supManufacturers {
            id
            name
            homepageUrl
            displayFlag
            isDistributorApi
            isVerified
          }
        }
        '''
        manufacturers = self.get_query(QUERY_MANUFACTURERS, variables)
        manufacturers = pd.DataFrame(manufacturers['supManufacturers'])
        manufacturers.to_csv(file_name, sep=',', encoding='utf-8')

        return manufacturers

    # func to get all attributes
    def get_all_attributes(self, file_name, variables=None):
        QUERY_ATTRIBUTES = '''
        query Attributes {
          supAttributes{
            group
            id
            name
            shortname
            unitsName
            unitsSymbol
            valueType
          }
        }
        '''
        attributes = self.get_query(QUERY_ATTRIBUTES, variables)
        attributes = pd.DataFrame(attributes['supAttributes'])
        attributes.to_csv(file_name, sep=',', encoding='utf-8')

        return attributes

    # func to obtain info about all sellers on octopart.com
    def get_all_sellers(self, file_name, variables=None):
        QUERY_SELLERS = '''
        query Sellers {
          supSellers {
            id
            name
            homepageUrl
            displayFlag
            isDistributorApi
            isVerified
          }
        }
        '''
        sellers = self.get_query(QUERY_SELLERS, variables)
        sellers = pd.DataFrame(sellers['supSellers'])
        sellers.to_csv(file_name, sep=',', encoding='utf-8')

        return sellers

    # if you want get some particular part-info
    def get_parts_by_id(self, variables :list, file_name):
        QUERY_PARTS = '''
        query Parts ($ids: [String!]!) {
          supParts(ids: $ids) {
            category{
              id
              name
            }
            id
            manufacturer {
              id
              name
              }
            name
            shortDescription
            }
          }
        '''
        assert type(variables) == list, 'The variables type should be list'
        variables = list([str(x) for x in variables])
        variables = {'ids': variables}

        parts = data.get_query(QUERY_PARTS, variables)
        parts = pd.DataFrame(parts['supParts'])
        parts.to_csv(file_name, sep=',', encoding='utf-8')

        return parts