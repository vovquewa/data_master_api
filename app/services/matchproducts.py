import os
import re
from pathlib import Path

import pandas as pd
from fuzzywuzzy import fuzz, process

from app.services.read_excel_f import FileFinder, HeaderFinder


def normalize_text(text):
    """Нормализация текста для сравнения"""
    text = str(text).lower()
    text = re.sub(r"[^\w\s/-]", " ", text)  # Удаляем спецсимволы
    text = re.sub(r"\s+", " ", text).strip()  # Удаляем лишние пробелы
    return text


def extract_attributes(text):
    """Извлечение атрибутов из названия товара"""
    text = str(text).lower()

    # 1. Тип продукта (первое слово)
    product_type = re.search(r"^([^\s]+)", text)
    product_type = product_type.group(1).replace(",", "") if product_type else None

    # 2. Артикул (разные форматы)
    product_code = None
    code_patterns = [
        r"\b[a-z]{2,4}\d{2,4}(?:[-\/]\d{2,5}){1,3}\b",  # JL126-12/05-25
        r"\b[a-z]{2,4}\d{2,4}(?:[-\/]\d{1,5}){0,2}\b",  # AB123-45/67
        r"\b\d{2,5}(?:[-\/]\d{2,5}){1,2}\b",  # 12-34-56
        r"\b[a-z]+\d+[a-z]*\b",  # ABC123
        r"\b\d+[a-z]+\d*\b",  # 123ABC
    ]

    for pattern in code_patterns:
        match = re.search(pattern, text)
        if match:
            product_code = re.sub(r"\s+", "", match.group()).upper()
            break

    # 3. Цвет
    color = None
    # if 'мультиколор' in text:
    #   color = 'мультиколор'
    # else:
    color_match = re.search(r"(?:цвет|колор|,)\s*([a-zа-яё]+)", text)
    if not color_match:
        color_match = re.search(r"(\b[a-zа-яё]+)(?=\s*\d{2}\b)", text)
    color = color_match.group(1).strip() if color_match else None

    # 4. Размер
    size = None
    size_patterns = [
        # 'standard':
        r"^(?P<size>\d{1,3}(?:,\d{1,2})?)(?:\s*см)?$",
        # 'range':
        r"^(?P<from>\d{2,3})[-–](?P<to>\d{2,3})(?:\s*см)?$",
        # 'clothing':
        r"^(?P<size>XS|S|M|L|XL|XXL|XXXL|XXXXL|XXXXXL|XXXXXXL)$",
        #'shoes':
        r"^(?P<size>\d{2}(?:,\d{1,2})?)$",
        #'combined':
        r"^(?P<num>\d+)\s*/\s*(?P<size>\d{2})$",
        # 'euro':
        r"^(?P<size>\d{2,3})\s*(?:EU|евро)$",
        #  'one_size':
        r"^(?P<size>one\s*size|универсальный|без\s*размера)$",
        #  'bedding':
        r"(?P<width>\d{2,3})[хx×](?P<length>\d{2,3})",
        # 'complex':
        r"(?P<width>\d{2,3})[хx×](?P<length>\d{2,3})[хx×](?P<height>\d{2,3})",
    ]
    for pattern in size_patterns:
        size_match = re.search(pattern, text)

        # size_match = re.search(r'(?:р|размер|size)\s*(\d{2})\b', text)
        if not size_match:
            size_match = re.search(r"\b(\d{2})\b(?!.*\d{2})", text)
    size = size_match.group(1) if size_match else None

    return {
        "product_type": product_type,
        "product_code": product_code,
        "size": size,
        "color": color,
    }


def match_products(df_order, df_supplier):
    """Основная функция сопоставления товаров"""

    # Нормализация текста
    df_order["normalized"] = df_order["Название"].apply(normalize_text)
    df_supplier["normalized"] = df_supplier["Номенклатура"].apply(normalize_text)

    # Извлечение атрибутов
    order_attrs = df_order["Название"].apply(extract_attributes).apply(pd.Series)
    supplier_attrs = (
        df_supplier["Номенклатура"].apply(extract_attributes).apply(pd.Series)
    )

    df_order = pd.concat([df_order, order_attrs], axis=1)
    df_supplier = pd.concat([df_supplier, supplier_attrs], axis=1)

    # 1. Точное совпадение по артикулу и размеру
    merged = pd.merge(
        df_order,
        df_supplier,
        on=["product_code", "size"],
        how="left",
        suffixes=("_order", "_supplier"),
    )

    # 2. Для несопоставленных - совпадение по артикулу
    unmatched = merged[merged["Номенклатура"].isna()].copy()
    if not unmatched.empty:
        #     temp_merged = pd.merge(
        #         unmatched[['Код ТМЦ', 'Название', 'product_code', 'size', 'color_order', 'normalized_order']],
        #         df_supplier,
        #         left_on='product_code',
        #         right_on='product_code',
        #         how='left'
        #     )
        temp_merged = unmatched[
            [
                "Код ТМЦ",
                "Название",
                "product_code",
                "size",
                "color_order",
                "normalized_order",
            ]
        ]

        merged = pd.concat(
            [merged[~merged["Номенклатура"].isna()], temp_merged], ignore_index=True
        )

    # 3. Для оставшихся - fuzzy matching
    still_unmatched = merged[merged["Номенклатура"].isna()].copy()
    if not still_unmatched.empty:
        matches = []
        for _, row in still_unmatched.iterrows():
            supplier_subset = (
                df_supplier[df_supplier["product_type"] == row["product_type_order"]]
                if pd.notna(row["product_type_order"])
                else df_supplier
            )

            if len(supplier_subset) > 0:
                best_match = process.extractOne(
                    row["normalized_order"],
                    supplier_subset["normalized"],
                    scorer=fuzz.token_set_ratio,
                    score_cutoff=90,
                )
                if best_match:
                    best_match_row = supplier_subset.iloc[best_match[2]]
                    matches.append(
                        {
                            "Код ТМЦ": row["Код ТМЦ"],
                            "Название": row["Название"],
                            "product_code": row["product_code"],
                            "size": row["size"],
                            "color": row["color_order"],
                            "Номенклатура": best_match_row["Номенклатура"],
                            "КИЗ": best_match_row.get("КИЗ", ""),
                            "BOOK_ID": best_match_row.get("BOOK_ID", ""),
                            "Метод": "Нечеткое",
                            "Уровень": best_match[1],
                        }
                    )

        if matches:
            matches_df = pd.DataFrame(matches)
            final = pd.concat(
                [merged[~merged["Номенклатура"].isna()], matches_df], ignore_index=True
            )
        else:
            final = merged[~merged["Номенклатура"].isna()].copy()
    else:
        final = merged

    # Форматирование результата
    result_cols = [
        "Код ТМЦ",
        "Название",
        "product_code",
        "size",
        "color",
        "Номенклатура",
        "КИЗ",
        "BOOK_ID",
        "Метод",
        "Уровень",
    ]

    result = (
        final[[col for col in result_cols if col in final.columns]]
        .rename(
            columns={
                "product_code": "Артикул",
                "size": "Размер",
                "color": "Цвет",
                "Номенклатура": "Сопоставленная номенклатура",
            }
        )
        .fillna("")
    )

    return result


def match():

    # путь к файлам откуда бурем данные
    home_dir = os.getcwd()
    # files_path = str(files_path)
    dir_rep = FileFinder("/".join([home_dir, "Общее"]))

    # по части строки ищем по части названия это файл с заказами или кодами,
    # создаем список с названиями столбцов для поиска шапки по названию колонок,
    # создаем копию класса для поиска шапки
    supppliers_files = dir_rep.find_files_by_partial_name("код")
    supplier_head = ["Номенклатура", "BOOK_ID", "КИЗ"]
    supHeaderFinder = HeaderFinder

    order_files = dir_rep.find_files_by_partial_name("заказ")
    order_head = ["№", "Код ТМЦ", "Название", "Кол-во", "Цена", "Сумма"]
    ordHeaderFinder = HeaderFinder
    try:
        # Загрузка данных

        df_order = pd.concat(
            [
                ordHeaderFinder(f, order_head).to_dataframe()[["Код ТМЦ", "Название"]]
                for f in order_files
            ]
        )
        df_supplier = pd.concat(
            [
                supHeaderFinder(f, supplier_head).to_dataframe()[supplier_head]
                for f in supppliers_files
            ]
        )

        # Сопоставление товаров
        matched_products = match_products(df_order, df_supplier)

        # Сохранение результатов
        matched_products.to_excel("matched_results.xlsx", index=False)
        print(f"Сопоставление завершено. Найдено {len(matched_products)} совпадений.")
        print("Результаты сохранены в matched_results.xlsx")

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")


if __name__ == "__main__":
    try:
        # Загрузка данных

        df_order = pd.concat(
            [
                ordHeaderFinder(f, order_head).to_dataframe()[["Код ТМЦ", "Название"]]
                for f in order_files
            ]
        )
        df_supplier = pd.concat(
            [
                supHeaderFinder(f, supplier_head).to_dataframe()[supplier_head]
                for f in supppliers_files
            ]
        )

        # Сопоставление товаров
        matched_products = match_products(df_order, df_supplier)

        # Сохранение результатов
        matched_products.to_excel("matched_results.xlsx", index=False)
        print(f"Сопоставление завершено. Найдено {len(matched_products)} совпадений.")
        print("Результаты сохранены в matched_results.xlsx")

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
