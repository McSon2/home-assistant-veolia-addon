import argparse
import requests
import xmltodict
import logging
from datetime import datetime
import xml.etree.ElementTree as ET
import operator
from copy import copy

_LOGGER = logging.getLogger(__name__)

FORMAT_DATE = "%Y-%m-%d"
DAILY = "DAILY"
MONTHLY = "MONTHLY"
HISTORY = "HISTORY"

class VeoliaClient:
    """Class to manage the webServices system."""

    def __init__(self, email: str, password: str, session=requests.Session(), abo_id="") -> None:
        """Initialize the client object."""
        self._email = email
        self._pwd = password
        self.__aboId = abo_id
        self.address = "https://www.service.eau.veolia.fr/icl-ws/iclWebService"
        self.headers = {"Content-Type": "application/xml; charset=UTF-8"}
        self.__tokenPassword = None
        self.success = False
        self.attributes = {DAILY: {}, MONTHLY: {}}
        self.session = requests.Session()
        self.__enveloppe = self.__create_enveloppe()

    def login(self):
        """Check if login is right.

        raise BadCredentialsException if not
        """
        try:
            _LOGGER.info("Check credentials")
            self._get_tokenPassword(check_only=True)
        except Exception as e:
            _LOGGER.error(f"wrong authentication : {e}")
            raise BadCredentialsException(f"wrong authentication : {e}")

    def update_all(self):
        """
        Return the latest collected datas.

        Returns:
            dict: dict of consumptions by date and by period
        """
        self.update()
        self.update(True)
        return self.attributes

    def update(self, month=False):
        """
        Return the latest collected datas by arg.

        Args:
            month (bool, optional): if True returns consumption by Month else by Day. Defaults to False.

        Returns:
            dict: dict of consumptions by date
        """
        if self.__tokenPassword is None:
            self._get_tokenPassword()
        self._fetch_data(month)
        if not self.success:
            return
        period = MONTHLY if month is True else DAILY
        return self.attributes[period]

    def close_session(self):
        """Close current session."""
        self.session.close()
        self.session = None

    def _fetch_data(self, month=False):
        """Fetch latest data from Veolia."""
        _LOGGER.debug(f"_fetch_data by month ? {month}")
        period = MONTHLY if month is True else DAILY
        if month is True:
            action = "getConsommationMensuelle"
        else:
            action = "getConsommationJournaliere"
        _LOGGER.debug(f"action={action}")
        datas = self.__construct_body(action, {"aboNum": self.__aboId}, anonymous=False)

        resp = self.session.post(
            self.address,
            headers=self.headers,
            data=datas,
        )
        _LOGGER.debug(str(resp))
        _LOGGER.debug(str(resp.text))
        if resp.status_code != 200:
            msg = f"Error {resp.status_code} fetching data :"
            try:
                msg += xmltodict.parse(f"<soap:Envelope{resp.text.split('soap:Envelope')[1]}soap:Envelope>")[
                    "soap:Envelope"
                ]["soap:Body"]["soap:Fault"]["faultstring"]
            except Exception:
                msg += str(resp.text)
            _LOGGER.error(msg)
            raise Exception(f"{msg}")
        else:
            try:
                result = xmltodict.parse(f"<soap:Envelope{resp.text.split('soap:Envelope')[1]}soap:Envelope>")
                _LOGGER.debug(f"result_fetch_data={result}")
                lstindex = result["soap:Envelope"]["soap:Body"][f"ns2:{action}Response"]["return"]
                self.attributes[period][HISTORY] = []

                if month is True:
                    if isinstance(lstindex, list):
                        lstindex.sort(key=operator.itemgetter("annee", "mois"), reverse=True)
                        for val in lstindex:
                            self.attributes[period][HISTORY].append(
                                (
                                    f"{val['annee']}-{val['mois']}",
                                    int(val["consommation"]),
                                )
                            )
                    elif isinstance(lstindex, dict):
                        self.attributes[period][HISTORY].append(
                            (
                                f"{lstindex['annee']}-{lstindex['mois']}",
                                int(lstindex["consommation"]),
                            )
                        )
                else:
                    if isinstance(lstindex, list):
                        lstindex.sort(key=operator.itemgetter("dateReleve"), reverse=True)
                        for val in lstindex:
                            self.attributes[period][HISTORY].append(
                                (
                                    datetime.strptime(val["dateReleve"], FORMAT_DATE).date(),
                                    int(val["consommation"]),
                                )
                            )
                        self.attributes["last_index"] = int(lstindex[0]["index"]) + int(lstindex[0]["consommation"])
                    elif isinstance(lstindex, dict):
                        self.attributes[period][HISTORY].append(
                            (
                                datetime.strptime(lstindex["dateReleve"], FORMAT_DATE).date(),
                                int(lstindex["consommation"]),
                            )
                        )
                        self.attributes["last_index"] = int(lstindex["index"]) + int(lstindex["consommation"])
                self.success = True
            except ValueError:
                raise VeoliaError("Issue with accessing data")
                pass

    def _get_tokenPassword(self, check_only=False):
        """Get token password for next actions who needs authentication."""
        datas = self.__construct_body(
            "getAuthentificationFront",
            {"cptEmail": self._email, "cptPwd": self._pwd},
            anonymous=True,
        )
        resp = self.session.post(
            self.address,
            headers=self.headers,
            data=datas,
        )
        _LOGGER.debug(f"resp status={resp.status_code}")
        if resp.status_code != 200:
            _LOGGER.error("problem with authentication")
            raise Exception(f"POST /__get_tokenPassword/ {resp.status_code}")
        else:
            result = xmltodict.parse(f"<soap:Envelope{resp.text.split('soap:Envelope')[1]}soap:Envelope>")
            _LOGGER.debug(f"result_getauth={result}")
            if check_only:
                return None
            self.__tokenPassword = result["soap:Envelope"]["soap:Body"]["ns2:getAuthentificationFrontResponse"][
                "return"
            ]["espaceClient"]["cptPwd"]
            contrat = result["soap:Envelope"]["soap:Body"]["ns2:getAuthentificationFrontResponse"]["return"][
                "listContrats"
            ]

            if self.__aboId == "":
                _LOGGER.debug("No Abo_ID provided, finding first")
                if isinstance(contrat, list):
                    self.__aboId = contrat[0]["aboId"]
                else:
                    self.__aboId = contrat["aboId"]
            _LOGGER.debug(f"__aboId={self.__aboId}")

    def __create_enveloppe(self):
        """Return enveloppe for requests.

        Returns:
            xml: enveloppe
        """
        __enveloppe = ET.Element("soap:Envelope")
        __enveloppe.set("xmlns:soap", "http://schemas.xmlsoap.org/soap/envelope/")
        __enveloppe.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
        __header = ET.SubElement(__enveloppe, "soap:Header")
        __security = ET.SubElement(__header, "wsse:Security")
        __security.set(
            "xmlns:wsse",
            "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd",
        )
        __security.set(
            "xmlns:wsu",
            "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd",
        )
        __usernameToken = ET.SubElement(__security, "wsse:UsernameToken")
        __usernameToken.set(
            "xmlns:wsu",
            "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd",
        )
        __usernameToken.set("wsu:Id", "UsernameToken-aiehdbsf52")
        __username = ET.SubElement(__usernameToken, "wsse:Username")
        __username.text = "anonyme"
        __password = ET.SubElement(__usernameToken, "wsse:Password")
        __password.set(
            "Type",
            "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText",
        )
        __password.text = "PYg6fMplCoo19dZVXkn2"
        __nonce = ET.SubElement(__usernameToken, "wsse:Nonce")
        __nonce.set(
            "EncodingType",
            "http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-soap-message-security-1.0#Base64Binary",
        )
        __nonce.text = "1dWl+HzD/sJsWzAcDHQX6Q=="
        __created = ET.SubElement(__usernameToken, "wsse:Created")
        __created.text = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        ET.SubElement(__enveloppe, "soap:Body")
        return __enveloppe

    def __construct_body(self, action: str, elts: dict, anonymous=True):
        """Append action into a copy of _enveloppe.

        Args:
            action (str): Name of action
            elts (dict): elements to insert into action
            anonymous (bool, optional): anonymous authentication. Defaults to True.

        Returns:
            xml: completed enveloppe for requests
        """
        datas = copy(self.__enveloppe)
        _body = datas.find("soap:Body")
        _action = ET.SubElement(_body, f"ns2:{action}")
        _action.set("xmlns:ns2", "http://ws.icl.veolia.com/")
        for k, v in elts.items():
            t = ET.SubElement(_action, k)
            t.text = v

        if not anonymous:
            username_token = datas.find("soap:Header").find("wsse:Security").find("wsse:UsernameToken")
            username_token.find("wsse:Username").text = self._email
            username_token.find("wsse:Password").text = self.__tokenPassword

        return ET.tostring(datas, encoding="UTF-8")

def send_data_to_home_assistant(sensor_name, state, attributes, token):
    url = f"http://supervisor/core/api/states/{sensor_name}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    data = {
        "state": state,
        "attributes": attributes
    }
    response = requests.post(url, headers=headers, json=data)
    _LOGGER.info(f"Data sent to Home Assistant: {response.status_code}, {response.text}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--email", required=True, help="Veolia account email")
    parser.add_argument("--password", required=True, help="Veolia account password")
    parser.add_argument("--abo_id", required=True, help="Veolia contract ID")
    parser.add_argument("--token", required=True, help="Home Assistant long-lived access token")
    args = parser.parse_args()

    client = VeoliaClient(args.email, args.password, abo_id=args.abo_id)
    client.login()
    data = client.update_all()

    # Process and send data to Home Assistant
    daily_consumption = data[DAILY][HISTORY][0][1]
    attributes = {
        "device_class": "water",
        "state_class": "total_increasing",
        "unit_of_measurement": "L",
        "friendly_name": "Veolia Water Consumption"
    }
    send_data_to_home_assistant("sensor.veolia_water_consumption", daily_consumption, attributes, args.token)
