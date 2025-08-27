PERMITTED_FIELDS = ["price", "description", "stock"]
def edit_product_info(item: dict, details: dict):
    for key, value in details.items():
        if key in PERMITTED_FIELDS:
            item[key] = value
    return item