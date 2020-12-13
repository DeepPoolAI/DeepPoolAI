import json
from urllib.request import urlopen
from IPython.display import clear_output
import pandas as pd
import dicttoxml
from xml.dom.minidom import parseString

class PoolAddressParser:

    def __init__(self, key):
        """

        Parameters
        ----------
        key : string
            Bing API key
        """
        self.key = key
        self.addresses = []

    def get_addresses(self, pools_coord: list, verbose: bool):
        """ Uses bing api to reverse-geocode lat long coordinates to usable addresses. If API responds with status
        code different than 200 (success), this lat long coordinate is skipped and counted as an error.

        Parameters
        ----------
        pools_coord : list
            This list should contain lat long coordinates of detected pools.
            Example:
                    [[36.2798, -115.1672]]
        verbose : bool
            Specifies if progress should be displayed. Useful for long 'pools_coord' lists.

        Returns
        -------
        pools_addresses: list
            This list contains addresses of pools specified if 'pools_coord'
            Example:
                    [{
                        "addressLine": "6513 Summer Bluff Ct",
                        "adminDistrict": "NV",
                        "adminDistrict2": "Clark Co.",
                        "countryRegion": "United States",
                        "formattedAddress": "6513 Summer Bluff Ct, North Las Vegas, NV 89084",
                        "intersection": {
                            "baseStreet": "Summer Bluff Ct",
                            "secondaryStreet1": "Evening Bluff Pl",
                            "intersectionType": "Near",
                            "displayName": "Summer Bluff Ct and Evening Bluff Pl"
                        },
                        "locality": "El Dorado",
                        "postalCode": "89084"
                    }]

        """

        pools_addresses = []
        _errors = 0
        n = len(pools_coord)
        for i in range(n):
            request_url = f"http://dev.virtualearth.net/REST/v1/Locations/{pools_coord[i][0]},{pools_coord[i][1]}?o&key={self.key}"
            request = urlopen(request_url)

            response_json = json.loads(request.read())
            if response_json["statusCode"] == 200:
                pool_data = {
                    "coordinates": pools_coord[i],
                    "address": response_json['resourceSets'][0]['resources'][0]['address']
                }
                pools_addresses.append(pool_data)
            elif verbose:
                _errors += 1

            if verbose:
                clear_output(wait=True)
                print(f"Reverse-geocoding progress {round(((i+1)/n)*100,1)}%  {i+1}/{n}")
                print("[{:<50}]".format("#"*(round((i+1)/n*100)//2)))
                print("Errors: ", _errors)

        self.addresses = pools_addresses

        return pools_addresses

    def write_to_json(self, file_name, pools_addresses = None):
        """

        Writes pools_addresses to json file

        Parameters
        ----------
        file_name: string
        pools_addresses: list
            optional
            If no list is given uses one that was result of last get_addresses function

        Returns None
        """

        if pools_addresses is None:
            pools_addresses = self.addresses

        with open(file_name, 'w') as fout:
            json.dump(pools_addresses, fout, indent=2)

        return
    
    def write_to_csv(self, file_name, pools_addresses = None):
        """
        Writes pools_addresses to csv file

        Parameters
        ----------
        file_name: string
        pools_addresses: list
            optional
            If no list is given uses one that was result of last get_addresses function

        Returns None
        -------
        """

        if pools_addresses is None:
            pools_addresses = self.addresses

        df = pd.json_normalize(pools_addresses)

        df.to_csv(file_name)
        return

    def write_to_xml(self, file_name, pools_addresses = None):
        """
        Writes pools_addresses to csv file

        Parameters
        ----------
        file_name: string
        pools_addresses: list
            optional
            If no list is given uses one that was result of last get_addresses function

        Returns None
        -------
        """

        if pools_addresses is None:
            pools_addresses = self.addresses

        xml = dicttoxml.dicttoxml(pools_addresses, attr_type=False)

        dom = parseString(xml)

        with open(file_name, 'w') as fout:
            fout.write(dom.toprettyxml())
        return
        
    
    def write_to_txt(self, file_name, pools_addresses = None):
        """
        Writes pools_addresses to csv file

        Parameters
        ----------
        file_name: string
        pools_addresses: list
            optional
            If no list is given uses one that was result of last get_addresses function

        Returns None
        -------
        """

        if pools_addresses is None:
            pools_addresses = self.addresses

        formattedAddress = [p["address"]["formattedAddress"] for p in pools_addresses]

        with open(file_name, 'w') as fout:
            fout.write('\n'.join(formattedAddress))

        return
