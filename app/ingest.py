import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def load_orders():
    """Load orders.csv and turn each row into one text chunk."""
    df = pd.read_csv(os.path.join(DATA_DIR, "orders.csv"))
    chunks = []
    for _, row in df.iterrows():
        text = (
            f"Order {row['order_id']}: customer {row['customer_id']} ordered "
            f"{row['product']} on {row['order_date']} for ${row['amount']}. "
            f"Status: {row['status']}."
        )
        chunks.append({
            "text": text,
            "doc_type": "orders",
            "record_id": row["order_id"]
        })
    return chunks


def load_refunds():
    """Load refunds.csv and turn each row into one text chunk."""
    df = pd.read_csv(os.path.join(DATA_DIR, "refunds.csv"))
    chunks = []
    for _, row in df.iterrows():
        text = (
            f"Refund {row['refund_id']} for order {row['order_id']} on "
            f"{row['refund_date']}: reason - {row['reason']}. "
            f"Amount refunded: ${row['amount']}. Status: {row['status']}."
        )
        chunks.append({
            "text": text,
            "doc_type": "refunds",
            "record_id": row["refund_id"]
        })
    return chunks


def load_support_tickets():
    """Load support_tickets.txt and split into one chunk per ticket block."""
    path = os.path.join(DATA_DIR, "support_tickets.txt")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = content.strip().split("\n\n")
    chunks = []
    for block in blocks:
        if not block.strip():
            continue
        # Try to extract TICKET_ID for record_id; fall back to first line
        ticket_id = "UNKNOWN"
        for line in block.splitlines():
            if line.startswith("TICKET_ID:"):
                ticket_id = line.split(":", 1)[1].strip()
                break
        chunks.append({
            "text": block.strip(),
            "doc_type": "support_tickets",
            "record_id": ticket_id
        })
    return chunks


def load_all_documents():
    """Combine all document types into one master chunk list."""
    all_chunks = []
    all_chunks.extend(load_orders())
    all_chunks.extend(load_refunds())
    all_chunks.extend(load_support_tickets())
    return all_chunks


if __name__ == "__main__":
    docs = load_all_documents()
    print(f"Total chunks loaded: {len(docs)}")
    for d in docs[:3]:
        print(d)