import json
import sys
import copy
import os
from g_drive_module import gdrive
from datetime import date
import pandas as pd


cmd = 'color 5E'
os.system(cmd)
os.system("mode con cols=110 lines=30")

today = date.today()
month = str(today.month)
year = str(today.year)

month_dict = {"0": "start reading",
              "1": "January",
              "2": "February",
              "3": "March",
              "4": "April",
              "5": "May",
              "6": "June",
              "7": "July",
              "8": "August",
              "9": "September",
              "10": "October",
              "11": "November",
              "12": "December"}


def clean_console():
    os.system('cls' if os.name == 'nt' else 'clear')


def open_menu():
    with open("menu/menu_dict.json") as file:
        menu = json.load(file)
        return menu


def print_menu(obj_level, main_level=""):
    print(50 * " ", main_level)
    # print("".join(str(key) + ": " + str(value) + (7 * " ") for key, value in menu_dict[level].items()) + "\n")
    string_menu = ""
    for key, value in menu_dict[obj_level].items():
        string_menu += "".join(str(key) + ": " + str(value) + (7 * " "))
    print(string_menu)


def choice_user():
    choice_user_0 = input("Choice: ").upper()
    return choice_user_0


def open_counters_db(data_base_id):
    with open(f"Counters_Database/{data_base_id}.json") as file:
        dict = json.load(file)
        return dict


def store_db(data_base_id, dict):
    with open(f"Counters_Database/{data_base_id}.json", 'w') as file:
        json.dump(dict, file)


def store_menu(dict):
    with open("menu/menu_dict.json", 'w') as file:
        json.dump(dict, file)


def inc_input():
    print("\nНе верный ввод, попробуйте снова")


def float_check(input_user):
    try:
        float(input_user)
    except:
        return False
    else:
        return float(input_user)


def enter_reading(dict_er_year):

    dict_er = dict_er_year[year]
    # ввод месяца в ручном или автоматическом режиме, на выходе получается {год: {'месяц': {}}}
    while True:
        dict_er = dict_er_year[year]
        new_month = input("Choice: ")
        # проверка на формат ввода номера месяца:
        if new_month.upper() == "B":
            return None
        elif new_month == "":
            new_month = month
        if new_month in month_dict:
            # проверка на повторяющийся месяц:
            if new_month in dict_er:
                print("The meter reading for the specified month has already been entered")
                print("Do you want to change it?")
                print()
                change_data = input("(Y / N): ").upper()
                if change_data == "Y":
                    dict_er[new_month] = {}
                    break
            else:
                dict_er[new_month] = {}
                break
        else:
            inc_input()

    while True:
        data_meter = input("Input meter reading: ")
        print()
        if float_check(data_meter):
            data_meter = float(data_meter)
            dict_er[new_month]["Meter reading: "] = data_meter
            break
        else:
            inc_input()
    # упорядочивание словаря, если номер нового месяца введен не попорядку
    list_keys = list(dict_er.keys())
    list_keys.sort(key=int)
    ordered_dict = {}
    for x in list_keys:
        ordered_dict[x] = dict_er[x]
    dict_er = copy.copy(ordered_dict)
    # форма подсчета:
    # подсчет потребления и стоимости если есть записи в словаре
    y = 0
    dict_temp = open_counters_db(data_base_id[:-2] + "TAR")
    tarif_metter = dict_temp[data_base_id]
    print("data_base_id[3:]", data_base_id[3:])
    cons_str = ""
    if data_base_id[3:] == "WM":
        cons_str = "(m3)"
    elif data_base_id[3:] == "EM":
        cons_str = "(kW)"
    elif data_base_id[3:] == "HM":
        cons_str = "(Gcal)"

    for x in list(dict_er.keys())[-2::-1]:
        y = y - 1
        # потребление
        consumption_minuend = dict_er[list(dict_er.keys())[y]]["Meter reading: "]
        consumption_subtrahend = dict_er[x]["Meter reading: "]
        consumption = round((consumption_minuend - consumption_subtrahend), 3)
        # внесение данных потребления в словарь
        dict_er[list(dict_er.keys())[y]][f"Consumption {cons_str}: "] = consumption
        # подсчет стоимости
        coast_water_consumption = round((tarif_metter * consumption), 2)
        # внесение данных в словарь
        dict_er[list(dict_er.keys())[y]]["Coast (hrn): "] = coast_water_consumption
        dict_er_year[year] = dict_er
    return dict_er_year


def check_new_obj_name():
    while True:

        print("\n(OBJECT NAME must contain a min of 3 and a max of 15 letters)\n(first 3 characters only letters)")
        new_obj_name = input("\nINPUT NEW OBJECT NAME: ").upper()
        if new_obj_name == "B":
            break

        elif len(new_obj_name) <= 15:
            if all(x.isalpha() or x.isspace() for x in new_obj_name):
                if new_obj_name[:3].isalpha():
                    if new_obj_name[:3] in menu_dict["OBJECTS"].keys():
                        inc_input()
                        print("The first 3 letters of the New Object are the same as the other objects")
                    else:
                        return new_obj_name
                else:
                    inc_input()
                    print("First 3 letters of the New Object name are not letters")
            else:
                inc_input()
        else:
            inc_input()
            print("New object name is longer than 15 characters")


def backup_bd():
    while True:
        # List of files DB in local directory
        local_list_bd = os.listdir(path="Counters_Database")
        print("List of files DB in local directory\n")
        for a, b, c, d in zip(local_list_bd[:5], local_list_bd[4:9], local_list_bd[8:13], local_list_bd[12:]):
            print('{:<15}{:<15}{:<15}{:<}'.format(a, b, c, d))
        print("\n"*2)

        # List files storage on gdrive
        gdrive_list_bd = gdrive.list_files_gdrive()
        print("List files storage on gdrive\n")
        for a, b, c, d in zip(local_list_bd[:5], local_list_bd[4:9], local_list_bd[8:13], local_list_bd[12:]):
            print('{:<15}{:<15}{:<15}{:<}'.format(a, b, c, d))
        print("\n" * 2)

        # List files with only id storage on gdrive
        del_gdrive_list_files_id = []
        for n in gdrive_list_bd:
            del_gdrive_list_files_id.append(n["id"])

        answer_save = input(8*"\n" + "Choice for REC: ")
        if answer_save.upper() == "U":
            gdrive.del_batch(del_gdrive_list_files_id)
            gdrive.create_file_v2(local_list_bd)
        elif answer_save.upper() == "D":
            gdrive.download_file(gdrive_list_bd)
        elif answer_save.upper() == "B":
            break


def table_dict_v2(dict):
    for x, y in dict.items():
        print(x)
        panda = pd.DataFrame(y)
        print(panda)
        print()


# Menu
menu_dict = open_menu()

while True:

    while True:
        # main "page"
        clean_console()

        print_menu("MAIN")
        for n in range(22):
            print()
        print_menu("OBJECTS", "OBJECTS")
        if len(menu_dict["OBJECTS"]) == 0:
            print(43 * " ", "OBJECTS NOT CREATED")
        print()
        print()
        ch_us = choice_user()

        data_base_id = ""
        if ch_us in list(menu_dict["MAIN"].keys()):
            if ch_us == "E":
                sys.exit(0)

            elif ch_us == "REC":
                clean_console()
                print("B: BACK" + 15*" " + "U: Upload DB to Gdrive" + 15*" " + "D: Download DB from Gdrive\n")
                print(46*" " + "BACKUP & RECOVERY")
                backup_bd()

            # Settings menu
            elif ch_us == "ST":

                while True:
                    clean_console()
                    print_menu("SETTINGS")
                    for n in range(26):
                        print()
                    ch_us = choice_user()

                    if ch_us in list(menu_dict["SETTINGS"].keys()):

                        # Создание нового объекта
                        if ch_us == "NEW":
                            # проверка требований к новому имени
                            clean_console()
                            print("B: BACK ")
                            for n in range(23):
                                print()
                            new_obj_name = check_new_obj_name()
                            if new_obj_name == None:
                                continue
                            else:
                                # создание объекта в меню ключ: значение (первые 3 буквы: новое имя)
                                menu_dict["OBJECTS"][new_obj_name[:3]] = new_obj_name

                                # и сохранение нового меню
                                store_menu(menu_dict)

                                # создание базы данных объекта (базы счетчиков)
                                # создаем список видов (типов) учета (хол.вода, эл-во, отопление ('WM', 'EM', 'HM'))
                                list_name_counters = list(menu_dict["OBJECTS MENU"].keys())[:-1]

                                # cловари для бд
                                tar_db = {}
                                new_db = {}
                                new_db[year] = {}

                                # создаем новое имя базы данных путем сложения первых 3 букв нового и типов учета
                                for x in list_name_counters:
                                    new_db_name = new_obj_name[:3] + x
                                    print(new_db_name)
                                    # создаем и сохраняем на диске
                                    # бд учета
                                    store_db(new_db_name, new_db)
                                    # значения бд тарифов
                                    tar_db[new_db_name] = 0

                                # сохранение бд тарифов
                                store_db(new_obj_name[:3] + "TAR", tar_db)
                                print(f"Object {new_obj_name} created successfully")

                        # Удаление объекта
                        elif ch_us == "DEL":
                            while True:
                                clean_console()
                                print("B: BACK ")
                                for n in range(22):
                                    print()
                                print_menu("OBJECTS", "OBJECTS")
                                print()
                                if len(menu_dict["OBJECTS"]) == 0:
                                    print(43 * " ", "OBJECTS NOT CREATED")
                                print()
                                print("Input first 3 letters of deleting objects")
                                print()
                                del_obj_choice = input("Сhoice: ").upper()

                                if del_obj_choice in list(menu_dict["OBJECTS"].keys()):
                                    # удаление объекта из меню и сохранение обновленного меню
                                    # удаление пунктов из меню
                                    del menu_dict["OBJECTS"][del_obj_choice]
                                    # сохранение обновленного меню на диск
                                    store_menu(menu_dict)

                                    # удаление баз данных объекта:
                                    # удаление файла с тарифами объекта
                                    os.remove(f'Counters_Database//{del_obj_choice + "TAR"}.json')

                                    list_name_counters = list(menu_dict["OBJECTS MENU"].keys())[:-1]
                                    for x in list_name_counters:
                                        del_db_name = del_obj_choice + x
                                        file_path = f'Counters_Database/{del_db_name}.json'
                                        os.remove(file_path)
                                    print("Object deleted successfully")
                                    continue
                                elif del_obj_choice == "B":
                                    break
                                else:
                                    inc_input()
                        elif ch_us == "B":
                            break
                    else:
                        inc_input()


        if ch_us in list(menu_dict["OBJECTS"].keys()):
            # подменю для действующих объектов одинаково
            # запись кода для идентификации базы данных определенного объекта
            data_base_id = data_base_id + ch_us
            while True:
                # "OBJECTS MENU"
                # display
                clean_console()
                print_menu("OBJECTS MENU")
                for n in range(26):
                    print()
                ch_us = choice_user()

                if ch_us in list(menu_dict["OBJECTS MENU"].keys()):
                    if ch_us == "B":
                        data_base_id = ""
                        break
                    else:
                        data_base_id = data_base_id + ch_us
                        # "METER_MENU"
                        while True:
                            # display
                            clean_console()
                            # top string display
                            # ER: ENTER/CHANGE  READINGS
                            # DEL: DELETE READINGS
                            # TAR: TARIFFS       B: BACK

                            print_menu("METER MENU")
                            print("\n" * 2)

                            # открытие БД счетчика по ключу и присвоение словаря переменной
                            dict_temp = open_counters_db(data_base_id)
                            table_dict_v2(dict_temp)
                            print("\n" * 18)

                            ch_us = choice_user()

                            if ch_us in list(menu_dict["METER MENU"].keys()):

                                # ENTER/CHANGE READINGS ВВОД, ИЗМЕНЕНИЕ, РАСЧЕТ, СОХРАНЕНИЕ
                                if ch_us == "ER":
                                    # display
                                    clean_console()
                                    print("B: BACK")
                                    print("\n" * 2)
                                    # открытие БД счетчика по ключу и присвоение словаря переменной
                                    dict_temp = open_counters_db(data_base_id)
                                    table_dict_v2(dict_temp)
                                    print("\n" * 14)
                                    print('"0"     - the value of the counter before consumption')
                                    print("Number  - from 1 to 12 for month")
                                    print('"ENTER" - current month')
                                    print()

                                    # ввод месяца, расчет потребления, сохранения новых данных в словарь
                                    dict_temp = enter_reading(dict_temp)
                                    if dict_temp == None:
                                        continue
                                    else:
                                        # сохранение словаря в файл
                                        store_db(data_base_id, dict_temp)
                                        dict_temp = {}


                                # "DELETE READINGS"
                                elif ch_us == "DEL":
                                    while True:
                                        # display
                                        clean_console()
                                        print("B: BACK")
                                        print("\n" * 2)
                                        # открытие БД счетчика по ключу и присвоение словаря переменной
                                        dict_temp = open_counters_db(data_base_id)
                                        table_dict_v2(dict_temp)
                                        print("\n" * 14)
                                        print("Input number of month for delete")
                                        print()

                                        del_obj_choice = input("Delete month: ")
                                        if del_obj_choice in list(dict_temp[year].keys()):
                                            del dict_temp[year][del_obj_choice]
                                            store_db(data_base_id, dict_temp)
                                            dict_temp = {}
                                            break
                                        elif del_obj_choice.upper() == "B":
                                            break
                                        else:
                                            inc_input()

                                #  "TAR": "TARIFFS"
                                elif ch_us == "TAR":
                                    dict_temp = open_counters_db(data_base_id[:-2] + "TAR")

                                    clean_console()
                                    print()
                                    print("B: BACK")
                                    print()
                                    print("CURRENT TARIFF: ", dict_temp[data_base_id])
                                    for n in range(20):
                                        print()

                                    print()
                                    tarif_metter = input("SET TARIFF: ")

                                    if float_check(tarif_metter):
                                        tarif_metter = float_check(tarif_metter)
                                        dict_temp[data_base_id] = tarif_metter
                                    print("New tariff", dict_temp[data_base_id])
                                    store_db(data_base_id[:-2] + "TAR", dict_temp)

                                # "BACK"
                                elif ch_us == "B":
                                    data_base_id = data_base_id[: -2]
                                    break
                            else:
                                inc_input()
                else:
                    inc_input()
        else:
            inc_input()

