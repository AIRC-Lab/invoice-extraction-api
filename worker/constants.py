PROMPT = """
You are an expert in extracting information from invoices. 
Extract the information from the invoice image provided:

Return the extracted information as a JSON object. If a field is not found, use null.
Example JSON structure:
{
    "Type": "Invoice",
    "No": "15021160",
    "Date": "26/04/2025",
    "Customer": "GROWTHEUM CAPITAL PARTNERS PTE. LTD.",
    "Supplier": "FUJIFILM Business Innovation Singapore Pte. Ltd.",
    "Currency": "SGD",
    "Ex rate": null,
    "Ex rate to SGD": null,
    "Project code": "FMC",
    "Tax type": "9% GST",
    "Description": [
        {
            "text": "F1C35070ST-4T S/N : 104683 - M1-TOTAL COL",
            "Amount (before tax)": 88.16,
            "Tax amount": 7.93,
            "Amount (after GST)": 96.09,
            "Amount in SGD": 88.16,
            "Tax amount in SGD": 7.93,
            "Amount after tax in SGD": 96.09
        },
        {
            "text": "F1C35070ST-4T S/N : 10232283 - M2-TOTAL B/W",
            "Amount (before tax)": 4.66,
            "Tax amount": 0.42,
            "Amount (after GST)": 5.08,
            "Amount in SGD": 4.66,
            "Tax amount in SGD": 0.42,
            "Amount after tax in SGD": 5.08
        }
    ]
}
"""