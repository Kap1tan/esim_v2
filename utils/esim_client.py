# utils/esim_client.py

import requests
import json
import logging
from typing import Dict, List, Optional, Any, Union
import uuid

# Настройка логирования
logger = logging.getLogger(__name__)


class ESIMAccessClient:
    """
    Класс для работы с API eSIM Access
    """

    def __init__(self, access_code: str):
        """
        Инициализация клиента API eSIM Access

        :param access_code: Access Code для API eSIM Access
        """
        self.base_url = "https://api.esimaccess.com/api/v1/open"
        self.headers = {
            "RT-AccessCode": access_code,
            "Content-Type": "application/json"
        }

    def get_packages_by_country(self, country_code: str) -> List[Dict[str, Any]]:
        """
        Получение тарифов для конкретной страны

        :param country_code: Код страны (ISO)
        :return: Список доступных пакетов
        """
        endpoint = f"{self.base_url}/package/list"
        payload = {
            "locationCode": country_code,
            "type": "",
            "packageCode": "",
            "slug": "",
            "iccid": ""
        }

        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                data=json.dumps(payload)
            )
            response.raise_for_status()
            result = response.json()

            if result.get("success"):
                return result.get("obj", {}).get("packageList", [])
            else:
                logger.error(f"Ошибка API: {result.get('errorMsg')}")
                return []
        except Exception as e:
            logger.error(f"Ошибка запроса: {e}")
            return []

    def order_profile(self, package_code: str, price: float, count: int = 1) -> Optional[str]:
        """
        Заказ eSIM профиля

        :param package_code: Код пакета
        :param price: Цена пакета
        :param count: Количество
        :return: Номер заказа или None в случае ошибки
        """
        endpoint = f"{self.base_url}/esim/order"
        transaction_id = f"WWS-{uuid.uuid4().hex[:8]}"
        amount = price * count

        payload = {
            "transactionId": transaction_id,
            "amount": amount,
            "packageInfoList": [
                {
                    "packageCode": package_code,
                    "count": count,
                    "price": price
                }
            ]
        }

        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                data=json.dumps(payload)
            )
            response.raise_for_status()
            result = response.json()

            if result.get("success"):
                return result.get("obj", {}).get("orderNo")
            else:
                logger.error(f"Ошибка заказа: {result.get('errorMsg')}")
                return None
        except Exception as e:
            logger.error(f"Ошибка запроса: {e}")
            return None

    def query_order(self, order_no: str) -> List[Dict[str, Any]]:
        """
        Запрос информации о заказе

        :param order_no: Номер заказа
        :return: Список eSIM профилей в заказе
        """
        endpoint = f"{self.base_url}/esim/query"
        payload = {
            "orderNo": order_no,
            "iccid": "",
            "pager": {
                "pageNum": 1,
                "pageSize": 10
            }
        }

        try:
            response = requests.post(
                endpoint,
                headers=self.headers,
                data=json.dumps(payload)
            )
            response.raise_for_status()
            result = response.json()

            if result.get("success"):
                return result.get("obj", {}).get("esimList", [])
            else:
                logger.error(f"Ошибка запроса заказа: {result.get('errorMsg')}")
                return []
        except Exception as e:
            logger.error(f"Ошибка запроса: {e}")
            return []