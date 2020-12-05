import json
from urllib.request import urlopen


class PoolAddressParser:

    def __init__(self, key):
        """

        Parameters
        ----------
        key : string
            Bing API key
        """
        self.key = key

    def get_addresses(self, pools_coord: list, verbose: bool = False):
        """

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

        for coord in pools_coord:
            request_url = f"http://dev.virtualearth.net/REST/v1/Locations/{coord[0]},{coord[1]}?o&key={self.key}"
            request = urlopen(request_url)

            response_json = json.loads(request.read())
            if response_json["statusCode"] == 200:
                address_json = response_json['resourceSets'][0]['resources'][0]['address']
                pools_addresses.append(address_json)
            elif verbose:
                pass

        return pools_addresses

    def write_to_csv(self, pools_addresses, file_name):
        """

        Parameters
        ----------
        pools_addresses
        file_name

        Returns
        -------

        """
