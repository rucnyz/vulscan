PERMITTED_FIELDS = ["price", "description", "stock"]
def edit_product_info(item: dict, details: dict):
    item.update(details)
    return item