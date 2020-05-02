#  Drakkar-Software OctoBot-Services
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.
from abc import abstractmethod

from octobot_trading.constants import REAL_TRADER_STR, SIMULATOR_TRADER_STR
from octobot_commons.enums import MarkdownFormat
from octobot_commons.pretty_printer import open_order_pretty_printer
from octobot_services.notification.notification import Notification
from octobot_services.enums import NotificationLevel, NotificationCategory


class _OrderNotification(Notification):
    def __init__(self, text, evaluator_notification: Notification):
        super().__init__("", text, "", MarkdownFormat.IGNORE, NotificationLevel.INFO,
                         NotificationCategory.TRADES, evaluator_notification)

        self._build_text()

    @abstractmethod
    def _build_text(self):
        raise NotImplementedError("_build_text is not implemented")


class OrderCreationNotification(_OrderNotification):
    def __init__(self, evaluator_notification: Notification, dict_order: dict, exchange_name: str):
        self.dict_order = dict_order
        self.exchange_name = exchange_name.capitalize()
        super().__init__("Order creation", evaluator_notification)

    def _build_text(self):
        self.text = ""
        self.markdown_text = ""
        self.text += f"- {open_order_pretty_printer(self.exchange_name, self.dict_order, markdown=False)}"
        self.markdown_text += \
            f"- {open_order_pretty_printer(self.exchange_name, self.dict_order, markdown=True)}"


class OrderEndNotification(_OrderNotification):
    def __init__(self, order_previous_notification: Notification, dict_order_filled: dict, exchange_name: str,
                 dict_orders_canceled: list, trade_profitability: float, portfolio_profitability: float,
                 portfolio_diff: float, add_profitability: bool, is_simulated: bool):
        self.dict_order_filled = dict_order_filled
        self.exchange_name = exchange_name.capitalize()
        self.dict_orders_canceled = dict_orders_canceled
        self.trade_profitability = trade_profitability
        self.portfolio_profitability = portfolio_profitability
        self.portfolio_diff = portfolio_diff
        self.add_profitability = add_profitability
        self.is_simulated = is_simulated
        super().__init__("Order update", order_previous_notification)

    def _build_text(self):
        self.text = ""
        self.markdown_text = ""
        trader_type = SIMULATOR_TRADER_STR if self.is_simulated else REAL_TRADER_STR
        if self.dict_order_filled is not None:
            self.text += f"{trader_type}Order(s) filled : " \
                         f"\n- {open_order_pretty_printer(self.exchange_name, self.dict_order_filled)}"
            md_text = open_order_pretty_printer(self.exchange_name, self.dict_order_filled, markdown=True)
            self.markdown_text += f"*{trader_type}*Order(s) filled : \n-{md_text}"

        if self.dict_orders_canceled is not None and self.dict_orders_canceled:
            self.text += f"{trader_type}Order(s) canceled :"
            self.markdown_text += f"*{trader_type}*Order(s) canceled :"
            for dict_order in self.dict_orders_canceled:
                self.text += f"\n- {open_order_pretty_printer(self.exchange_name, dict_order)}"
                self.markdown_text += \
                    f"\n- {open_order_pretty_printer(self.exchange_name, dict_order, markdown=True)}"

        if self.trade_profitability is not None and self.add_profitability:
            self.text += f"\nTrade profitability : {'+' if self.trade_profitability >= 0 else ''}" \
                         f"{round(self.trade_profitability * 100, 4)}%"
            self.markdown_text += f"\nTrade profitability : *{'+' if self.trade_profitability >= 0 else ''}" \
                                  f"{round(self.trade_profitability * 100, 4)}%*"

        if self.portfolio_profitability is not None and self.add_profitability:
            self.text += f"\nPortfolio profitability : {round(self.portfolio_profitability, 4)}% " \
                         f"{'+' if self.portfolio_diff >= 0 else ''}{round(self.portfolio_diff, 4)}%"
            self.markdown_text += f"\nPortfolio profitability : `{round(self.portfolio_profitability, 4)}% " \
                                  f"{'+' if self.portfolio_diff >= 0 else ''}{round(self.portfolio_diff, 4)}%`"