from src.data.excel_loader import ExcelDataLoader

loader = ExcelDataLoader("data/Sales & Active Stores Data.xlsb")
data = loader.load_all()

print("Sheets:", loader.sheets)
print("Sales shape:", data["sales"].shape)
print("Active Store shape:", data["active_store"].shape)
print("Headers:", data["headers"].head())
