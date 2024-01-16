import os
import pandas
from datetime import datetime


if __name__ == "__main__":
    """
    Made in order to explore the data.
    
    Notes:
        "wide" type files are processed "long" type files
        only "long" type files indicate the product in question
        only "long" type files will be taken into account
    
    Objetives:
        earliest measure:   09-11-2021
        latest measure:     20-12-2019
        amount of files: 292
        amount of products: 220
        get amount of measures 
            total: 367215

            by company: 
                company     product_amount  measure_amount
                movistar    159             116368
                claro       110             64330
                Abcdin      103             22217
                entel       88              34058
                Ripley      124             31140
                Paris       129             32953
                Falabella   110             31205
                wom         52              15217
                Lider       81              14289
                vtr         8               4629
                macOnline   5               809

            by country: 
                CL (aka Chile)

            by offer type: 
                unlocked    354887
                postpaid_new_line   11261
                postpaid_portability 1067

         index  product_id  timestamp                                product country   company  product_group_id offer_type       price
        418936        3200 2019-12-21  motorola Moto Z3 Play 128GB + Gamepad      CL  movistar               951   unlocked  272.891840
        418937        3200 2019-12-22  motorola Moto Z3 Play 128GB + Gamepad      CL  movistar               951   unlocked  272.891840
        418938        3200 2019-12-23  motorola Moto Z3 Play 128GB + Gamepad      CL  movistar               951   unlocked  272.891840
        418939        3200 2019-12-24  motorola Moto Z3 Play 128GB + Gamepad      CL  movistar               951   unlocked  272.891840
        418940        3200 2019-12-25  motorola Moto Z3 Play 128GB + Gamepad      CL  movistar               951   unlocked  272.891840
        ...            ...        ...                                    ...     ...       ...               ...        ...         ...
        420294        3201 2021-10-24  motorola Moto Z3 Play 128GB + Gamepad      CL     claro               951   unlocked  227.408351
        420295        3201 2021-10-25  motorola Moto Z3 Play 128GB + Gamepad      CL     claro               951   unlocked  227.408351
        420296        3201 2021-10-26  motorola Moto Z3 Play 128GB + Gamepad      CL     claro               951   unlocked  227.408351
        420297        3201 2021-10-27  motorola Moto Z3 Play 128GB + Gamepad      CL     claro               951   unlocked  227.408351
        420298        3201 2021-10-28  motorola Moto Z3 Play 128GB + Gamepad      CL     claro               951   unlocked  227.408351

    """
    
    files = 0
    total_measures = 0
    company_res = {}
    country_res = {}
    offer_res = {}
    product_res = {}

    company_products = {}

    earliest_time = None
    latest_time = None

    for x in [1]:

        path = "./model_data/time_series_" + str(x)
        print(path)

        for name in os.listdir(path):

            # if "long" in name and "23" in name:
            if name == "long_product_group_id_23":

                files += 1

                content = pandas.read_pickle(f"{path}/{name}")
                print(f"{name}\n\n{content}")
                input(...)

                total_measures += len(content)

                timestamps = list(content.loc[:,"timestamp"])
                companies = list(content.loc[:,"company"])
                countries = list(content.loc[:,"country"])
                products = list(content.loc[:,"product"])
                offers = list(content.loc[:,"offer_type"])
                products_by_company = content[["company", "product"]].values.tolist()

                for x in timestamps:

                    if earliest_time == None and latest_time == None:
                        latest_time = earliest_time = x

                    if earliest_time < x:
                        earliest_time = x
                    
                    if latest_time > x:
                        latest_time = x

                for x in companies:
                    if x in company_res:
                        company_res[x] += 1
                    else:
                        company_res[x] = 1

                for x in countries:
                    if x in country_res:
                        country_res[x] += 1
                    else:
                        country_res[x] = 1

                for x in offers:
                    if x in offer_res:
                        offer_res[x] += 1
                    else:
                        offer_res[x] = 1

                for x in products:
                    if x in product_res:
                        product_res[x] += 1
                    else:
                        product_res[x] = 1

                for x in products_by_company:
                    if x[0] in company_products:
                        company_products[x[0]].append(x[1])
                    else:
                        company_products[x[0]] = []
                        company_products[x[0]].append(x[1])

    print(earliest_time)    # technically higher, since it passed the least amount of time since it happend
    print(latest_time)      # technically lower, since it happend the most amount of time since it happend

    print(files)
    # print(total_measures)

    print(f"Results by company: {company_res}")
    # print(f"Results by country: {country_res}")

    # for x in company_products:
    #     print(f"Company: {x}\tAmount of measures: {len(company_products[x])}\tAmount of products: {len(set(company_products[x]))}")
    print(f"Amount of different products: {len(product_res)}\tSum of products: {sum(product_res.values())}")
    print(f"Results by offer: {offer_res}")