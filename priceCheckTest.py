# coding:utf-8

"""
@Time   :2022/4/15
@Author :evan.fang
@File   :pricecheck.py
@Desc   :进行订单金额对比
"""

import requests


def check_test(nation='us', number=None):
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
        raise 'wrong nation'

    # try一下看请求是否正确返回
    try:
        requests.get(url=u, headers=header).raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise requests.exceptions.HTTPError("HTTP error:", e)
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
        raise ValueError('price does not match:', number)


pc = check_test()

if __name__ == '__main__':
    pc.check_test('au', 'R059434475')
