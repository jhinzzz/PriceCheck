# coding:utf-8

"""
@Time   :2022/4/15
@Author :evan.fang
@File   :pricecheck.py
@Desc   :进行订单金额对比
"""

import requests
from GetError import write_csv
from datetime import date, timedelta

day_interval = 1
check_days = []

au_url = "https://knight.castlery.com.au/spree/api/orders?q[state_eq]=complete&q[completed_at_gteq]="
us_url = "https://knight.castlery.co/spree/api/orders?q[state_eq]=complete&q[completed_at_gteq]="
sg_url = "https://knight.castlery.sg/spree/api/orders?q[state_eq]=complete&q[completed_at_gteq]="

au_headers = {"X-Spree-Token": "2d5e70fe4f8935043528e72b6d95e420033bbaa997db620a"}
us_headers = {"X-Spree-Token": "402739c0a152c319ea241683337f072f4ddc2716e6b80139"}
sg_headers = {"X-Spree-Token": "ba996565c969301070f4f472b5bb684be59f79818ea86586"}


class PriceCheck(object):
    order_count = 0
    error_count = 0
    errors = []
    nation = ['au', 'us', 'sg']

    def get_days(self):
        # 根据datetime来计算这几天的日期
        for i in range(1, day_interval+1):
            check_days.append(str(date.today() - timedelta(days=i)))
        print("check %s completed orders" % check_days)
        # 根据列表内的日期进行price_check
        # AU
        for days in check_days:
            url = au_url + days
            self.get_orders('au', requests.get(url=url, headers=au_headers).json())
        # US
        for days in check_days:
            url = us_url + days
            self.get_orders("us", requests.get(url=url, headers=us_headers).json())
        # SG
        for days in check_days:
            url = sg_url + days
            self.get_orders("sg", requests.get(url=url, headers=sg_headers).json())

        print("total orders count: %s" % self.order_count)
        print("error orders count: %s" % self.error_count)
        # 如果存在错误订单，则触发写csv
        if self.error_count > 0:
            write_csv(self.errors)
            # 抛出异常，由actions发邮件
            raise AssertionError('error orders not equals to 0')

    def get_orders(self, nation, response):
        try:
            print(response)
            for i in response["orders"]:
                self.order_count += 1
                number = i['number']
                # print("%s order:%s" % (nation, number))
                self.price_check(nation, number)
        except requests.exceptions.HTTPError as e:
            print("error occurred: ", e)
            return False

    def price_check(self, nation, number):
        if nation == 'au':
            u = "https://knight.castlery.com.au/spree/api/orders/" + number + "/oms"
            header = au_headers
        elif nation == 'us':
            u = "https://knight.castlery.co/spree/api/orders/" + number + "/oms"
            header = us_headers
        elif nation == 'sg':
            u = "https://knight.castlery.sg/spree/api/orders/" + number + "/oms"
            header = sg_headers
        else:
            print('wrong nation')
            return False

        # try一下看请求是否正确返回
        try:
            requests.get(url=u, headers=header).raise_for_status()
        except requests.exceptions.HTTPError as e:
            print("404:", e)
            # 将错误订单和国家塞入errors
            self.errors.append([nation, number])
            # 错误订单数+1
            self.error_count += 1
            # 不再进行下一步
            return False
        else:
            r = requests.get(url=u, headers=header).json()

        # 价格计算
        item_price = r['shipping_fee'] - r['shipping_fee_discount']
        tax_price = r['shipping_fee_tax']

        for item in r['lines']:
            item_price += item['unit_price'] * item['quantity'] - item['line_discount']
            tax_price += item['line_tax']

        total_price = item_price + tax_price
        total_price = float('%.2f' % total_price)  # 精度转换
        tax_price = float('%.2f' % tax_price)  # 精度转换

        if total_price == r['amount_total'] and tax_price == r['tax_amount_total']:
            # print('pass')
            return True
        else:
            print("%s-%s: %s is not equal to %s" % (nation, number, total_price, r['amount_total']))
            # 价格不对，将错误订单压入errors
            self.errors.append([nation, number])
            # 错误订单数+1
            self.error_count += 1
            return False

    def check_test(self, nation, number):
        if nation == 'au':
            u = "https://knight-test.castlery.com.au/spree/api/orders/" + number + "/oms"
            header = {'X-Spree-Token': '017060db65725b67d25062974e0fdae9533a05b8b3eee1f2'}
        elif nation == 'us':
            u = "https://knight-test.castlery.co/spree/api/orders/" + number + "/oms"
            header = {'X-Spree-Token': '96c9ee5529d7f912c65d2d321ec985e10d69b1bfd90391e4'}
        elif nation == 'sg':
            u = "https://knight-test.castlery.sg/spree/api/orders/" + number + "/oms"
            header = {'X-Spree-Token': 'f35b35a4f6c286c2b855ff8df12c113ee0e9a37e532ece41'}
        else:
            print('wrong nation')
            return False

        # try一下看请求是否正确返回
        try:
            requests.get(url=u, headers=header).raise_for_status()
        except requests.exceptions.HTTPError as e:
            print("404:", e)
            # 将错误订单和国家塞入errors
            self.errors.append([nation, number])
            # 错误订单数+1
            self.error_count += 1
            # 不再进行下一步
            return False
        else:
            r = requests.get(url=u, headers=header).json()

        # 价格计算
        item_price = r['shipping_fee'] - r['shipping_fee_discount']
        tax_price = r['shipping_fee_tax']

        for item in r['lines']:
            item_price += item['unit_price'] * item['quantity'] - item['line_discount']
            tax_price += item['line_tax']

        total_price = item_price + tax_price
        total_price = float('%.2f' % total_price)  # 精度转换
        tax_price = float('%.2f' % tax_price)  # 精度转换

        if total_price == r['amount_total'] and tax_price == r['tax_amount_total']:
            # print('pass')
            return True
        else:
            print("%s-%s: %s is not equal to %s" % (nation, number, total_price, r['amount_total']))
            # 价格不对，将错误订单压入errors
            self.errors.append([nation, number])
            # 错误订单数+1
            self.error_count += 1
            return False


pc = PriceCheck()

if __name__ == '__main__':
    pc.check_test('us', 'R914239077')
    for i in range(1, day_interval+1):
        print(i)
