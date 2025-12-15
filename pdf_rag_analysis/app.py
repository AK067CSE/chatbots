# import streamlit as st
# from pathlib import Path
# import json
# from datetime import datetime
# import tempfile
# import os
# import pandas as pd

# from src.advanced_rag import AdvancedRAGSystem
# from src.pdf_extractor import PDFExtractor
# from src.comparator import EnhancedDocumentComparator
# from src.report_generator import generate_all_reports
# from src.llm_chains import LLMChainOrchestrator, MultiTurnChatChain
# from src.config import settings
# import json


# st.set_page_config(
#     page_title="Advanced PDF Analysis Chatbot",
#     page_icon="📄",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )


# def initialize_session():
#     if 'rag_system' not in st.session_state:
#         st.session_state.rag_system = AdvancedRAGSystem()
#     if 'chat_chain' not in st.session_state:
#         st.session_state.chat_chain = MultiTurnChatChain()
#     if 'llm_orchestrator' not in st.session_state:
#         st.session_state.llm_orchestrator = LLMChainOrchestrator()
#     if 'uploaded_documents' not in st.session_state:
#         st.session_state.uploaded_documents = {}
#     if 'extracted_data' not in st.session_state:
#         st.session_state.extracted_data = []
#     if 'comparison_results' not in st.session_state:
#         st.session_state.comparison_results = None
#     if 'po_doc' not in st.session_state:
#         st.session_state.po_doc = None
#     if 'invoice_doc' not in st.session_state:
#         st.session_state.invoice_doc = None
#     if 'messages' not in st.session_state:
#         st.session_state.messages = []


# def extract_pdf_content(pdf_file):
#     extractor = PDFExtractor()
    
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
#         tmp_file.write(pdf_file.read())
#         tmp_path = tmp_file.name
    
#     try:
#         doc = extractor.extract_pdf(Path(tmp_path))
#         return doc, None
#     except Exception as e:
#         return None, str(e)
#     finally:
#         os.unlink(tmp_path)


# def display_document_summary(doc):
#     col1, col2, col3 = st.columns(3)
#     with col1:
#         st.metric("Document Type", doc.metadata.doc_type)
#     with col2:
#         st.metric("Total Items", len(doc.items))
#     with col3:
#         st.metric("Grand Total", f"${doc.total:,.2f}")
    
#     if doc.items:
#         st.subheader("Line Items")
#         items_data = []
#         for item in doc.items:
#             items_data.append({
#                 "SKU": item.item_no,
#                 "Description": item.description,
#                 "Qty": item.quantity,
#                 "Unit Price": f"${item.unit_price:.2f}",
#                 "Total": f"${item.total_price:.2f}"
#             })
#         st.dataframe(items_data, use_container_width=True)
    
#     st.subheader("Financial Summary")
#     fin_col1, fin_col2, fin_col3, fin_col4 = st.columns(4)
#     with fin_col1:
#         st.metric("Subtotal", f"${doc.subtotal:,.2f}")
#     with fin_col2:
#         st.metric("Tax", f"${doc.tax:,.2f}")
#     with fin_col3:
#         st.metric("Total", f"${doc.total:,.2f}")
#     with fin_col4:
#         st.metric("Vendor", doc.metadata.vendor_name)


# def handle_pdf_upload():
#     st.header("📤 Upload PDF Documents")
    
#     uploaded_files = st.file_uploader(
#         "Upload PDF files (PO or Invoice)",
#         type="pdf",
#         accept_multiple_files=True,
#         key="pdf_uploader"
#     )
    
#     if uploaded_files:
#         col1, col2 = st.columns([1, 1])
        
#         with col1:
#             if st.button("📥 Process Documents"):
#                 progress_bar = st.progress(0)
#                 status_text = st.empty()
                
#                 for idx, pdf_file in enumerate(uploaded_files):
#                     status_text.text(f"Processing {pdf_file.name}...")
                    
#                     doc, error = extract_pdf_content(pdf_file)
                    
#                     if error:
#                         st.error(f"Error processing {pdf_file.name}: {error}")
#                     else:
#                         doc_id = f"doc_{len(st.session_state.uploaded_documents)}"
#                         st.session_state.uploaded_documents[doc_id] = {
#                             'filename': pdf_file.name,
#                             'document': doc,
#                             'timestamp': datetime.now().isoformat()
#                         }
                        
#                         chunk_count = st.session_state.rag_system.add_document(doc, doc_id)
#                         st.session_state.extracted_data.append(doc)
                        
#                         st.success(f"✓ {pdf_file.name} - {chunk_count} chunks indexed")
                    
#                     progress_bar.progress((idx + 1) / len(uploaded_files))
                
#                 status_text.text("✓ Processing complete!")
    
#     if st.session_state.uploaded_documents:
#         st.subheader("Uploaded Documents")
#         for doc_id, doc_info in st.session_state.uploaded_documents.items():
#             with st.expander(f"📄 {doc_info['filename']}"):
#                 display_document_summary(doc_info['document'])


# def handle_document_comparison():
#     if len(st.session_state.extracted_data) >= 2:
#         st.header("🔍 Document Comparison & Analysis")
        
#         po_doc = None
#         invoice_doc = None
        
#         for doc in st.session_state.extracted_data:
#             if 'PURCHASE_ORDER' in doc.metadata.doc_type:
#                 po_doc = doc
#             elif 'PROFORMA_INVOICE' in doc.metadata.doc_type or 'INVOICE' in doc.metadata.doc_type:
#                 invoice_doc = doc
        
#         if po_doc and invoice_doc:
#             if st.button("Compare Documents", key="compare_btn"):
#                 comparator = EnhancedDocumentComparator()
#                 comparison = comparator.compare(po_doc, invoice_doc)
#                 st.session_state.comparison_results = comparison
#                 st.session_state.po_doc = po_doc
#                 st.session_state.invoice_doc = invoice_doc
            
#             if st.session_state.comparison_results:
#                 comparison = st.session_state.comparison_results
                
#                 col1, col2, col3, col4 = st.columns(4)
#                 with col1:
#                     st.metric("Matching Items", comparison.matching_items)
#                 with col2:
#                     st.metric("Discrepancies", comparison.discrepant_items)
#                 with col3:
#                     st.metric("Total Variance", f"${comparison.summary_metrics.grand_total_difference:,.2f}")
#                 with col4:
#                     variance_pct = (comparison.summary_metrics.grand_total_difference / comparison.summary_metrics.grand_total_po * 100) if comparison.summary_metrics.grand_total_po != 0 else 0
#                     st.metric("Variance %", f"{variance_pct:.2f}%")
                
#                 tab_summary, tab_quantity, tab_price, tab_alerts, tab_extracted = st.tabs(
#                     ["Summary", "Quantity Analysis", "Price Analysis", "Alerts", "Extracted Data"]
#                 )
                
#                 with tab_summary:
#                     if comparison.item_level_comparison:
#                         st.warning("⚠ Discrepancies Found")
#                         disc_data = []
#                         for disc in comparison.item_level_comparison:
#                             disc_data.append({
#                                 "Item": disc.item_no,
#                                 "Description": disc.description,
#                                 "PO Qty": disc.po_quantity,
#                                 "Invoice Qty": disc.invoice_quantity,
#                                 "PO Price": f"${disc.po_unit_price:.2f}",
#                                 "Invoice Price": f"${disc.invoice_unit_price:.2f}",
#                                 "Status": disc.status
#                             })
#                         st.dataframe(disc_data, use_container_width=True)
#                     else:
#                         st.success("No discrepancies found - documents match!")
                
#                 with tab_quantity:
#                     st.subheader("Quantity Comparison")
#                     st.info("Quantity analysis module coming soon")
                
#                 with tab_price:
#                     st.subheader("Price Analysis")
#                     if comparison.item_level_comparison:
#                         st.info("Price analysis details available from item comparison")
#                     else:
#                         st.info("No price discrepancies")
                
#                 with tab_alerts:
#                     st.subheader("Automated Alerts & Recommendations")
#                     st.info("Alert generation module coming soon")
                
#                 with tab_extracted:
#                     st.subheader("Extracted Document Data")
#                     st.info("Extracted data visualization coming soon")
#                     st.json({"po_doc": po_doc.metadata if po_doc else {}, "invoice_doc": invoice_doc.metadata if invoice_doc else {}})
                
#                 st.divider()
#                 st.subheader("Generate & Download Reports")
#                 if st.button("Generate All Reports"):
#                     with st.spinner("Generating reports..."):
#                         report_paths = generate_all_reports(comparison, settings.REPORTS_DIR, po_doc, invoice_doc)
#                         st.success("Reports generated!")
                        
#                         col1, col2, col3 = st.columns(3)
#                         for fmt, path in list(report_paths.items())[:3]:
#                             with open(path, 'rb') as f:
#                                 with col1 if fmt == 'json' else (col2 if fmt == 'csv' else col3):
#                                     st.download_button(
#                                         label=f"Download {fmt.upper()}",
#                                         data=f.read(),
#                                         file_name=Path(path).name,
#                                         mime="application/octet-stream"
#                                     )
                        
#                         col1, col2, col3 = st.columns(3)
#                         remaining = list(report_paths.items())[3:]
#                         for i, (fmt, path) in enumerate(remaining):
#                             with open(path, 'rb') as f:
#                                 with [col1, col2, col3][i % 3]:
#                                     st.download_button(
#                                         label=f"Download {fmt.upper()}",
#                                         data=f.read(),
#                                         file_name=Path(path).name,
#                                         mime="application/octet-stream"
#                                     )


# def handle_intelligent_chat():
#     st.header("💬 Intelligent Document Chat")
    
#     if not st.session_state.uploaded_documents:
#         st.info("Please upload PDF documents first to start chatting.")
#         return
    
#     st.subheader("Document Q&A")
    
#     query = st.text_input("Ask a question about your documents:", key="chat_input")
    
#     if query:
#         with st.spinner("Searching documents and generating response..."):
#             retrieved_results = st.session_state.rag_system.retrieve(query, top_k=5, use_fusion=True)
            
#             context_text = "\n\n".join([r['text'] for r in retrieved_results[:3]])
            
#             result = st.session_state.llm_orchestrator.process_query(query, context_text)
            
#             st.session_state.messages.append({
#                 "role": "user",
#                 "content": query,
#                 "timestamp": datetime.now().isoformat()
#             })
#             st.session_state.messages.append({
#                 "role": "assistant",
#                 "content": result['response'],
#                 "timestamp": datetime.now().isoformat()
#             })
    
#     if st.session_state.messages:
#         st.subheader("Conversation History")
#         for msg in st.session_state.messages:
#             if msg['role'] == 'user':
#                 st.write(f"**You:** {msg['content']}")
#             else:
#                 st.write(f"**Assistant:** {msg['content']}")
    
#     if st.button("Clear Chat History"):
#         st.session_state.messages = []
#         st.rerun()


# def handle_advanced_analysis():
#     st.header("🔬 Advanced Analysis")
    
#     if not st.session_state.comparison_results:
#         st.info("Please compare documents first.")
#         return
    
#     if st.button("Generate Detailed Analysis"):
#         with st.spinner("Analyzing documents..."):
#             analysis = st.session_state.llm_orchestrator.analyze_full_comparison(
#                 {
#                     'po_total': st.session_state.comparison_results.po_total,
#                     'invoice_total': st.session_state.comparison_results.invoice_total,
#                     'discrepancies': len(st.session_state.comparison_results.discrepancies)
#                 },
#                 [doc.raw_text[:500] for doc in st.session_state.extracted_data]
#             )
            
#             st.subheader("Analysis Report")
#             st.write(analysis['report'])
            
#             st.subheader("Document Summary")
#             st.write(analysis['summary'])


# def main():
#     initialize_session()
    
#     st.title("📊 Advanced PDF Analysis & Chat Bot")
#     st.markdown("*Extract, Compare, Analyze, and Chat with your PDF documents using Advanced RAG*")
    
#     tab1, tab2, tab3, tab4, tab5 = st.tabs([
#         "📤 Upload", "📋 Compare", "💬 Chat", "🔬 Analysis", "📊 Summary"
#     ])
    
#     with tab1:
#         handle_pdf_upload()
    
#     with tab2:
#         handle_document_comparison()
    
#     with tab3:
#         handle_intelligent_chat()
    
#     with tab4:
#         handle_advanced_analysis()
    
#     with tab5:
#         st.header("System Summary")
        
#         rag_summary = st.session_state.rag_system.get_summary()
#         col1, col2, col3 = st.columns(3)
        
#         with col1:
#             st.metric("Documents Indexed", rag_summary['documents'])
#         with col2:
#             st.metric("Total Chunks", rag_summary['chunks'])
#         with col3:
#             st.metric("Retrieval Methods", len(rag_summary['retrieval_methods']))
        
#         st.subheader("Retrieval Methods Available")
#         for method in rag_summary['retrieval_methods']:
#             st.write(f"✓ {method}")
        
#         st.subheader("Session Info")
#         st.write(f"Messages: {len(st.session_state.messages)}")
#         st.write(f"Uploaded Documents: {len(st.session_state.uploaded_documents)}")


# if __name__ == "__main__":
#     main()
import streamlit as st
from pathlib import Path
import json
from datetime import datetime
import tempfile
import os
import pandas as pd

from src.advanced_rag import AdvancedRAGSystem
from src.pdf_extractor import PDFExtractor
from src.comparator import EnhancedDocumentComparator
from src.report_generator import generate_all_reports
from src.llm_chains import LLMChainOrchestrator, MultiTurnChatChain
from src.config import settings

st.set_page_config(
    page_title="Advanced PDF Analysis Chatbot",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

def initialize_session():
    if 'rag_system' not in st.session_state:
        st.session_state.rag_system = AdvancedRAGSystem()
    if 'chat_chain' not in st.session_state:
        st.session_state.chat_chain = MultiTurnChatChain()
    if 'llm_orchestrator' not in st.session_state:
        st.session_state.llm_orchestrator = LLMChainOrchestrator()
    if 'uploaded_documents' not in st.session_state:
        st.session_state.uploaded_documents = {}
    if 'extracted_data' not in st.session_state:
        st.session_state.extracted_data = []
    if 'comparison_results' not in st.session_state:
        st.session_state.comparison_results = None
    if 'po_doc' not in st.session_state:
        st.session_state.po_doc = None
    if 'invoice_doc' not in st.session_state:
        st.session_state.invoice_doc = None
    if 'messages' not in st.session_state:
        st.session_state.messages = []

def extract_pdf_content(pdf_file):
    extractor = PDFExtractor()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(pdf_file.read())
        tmp_path = tmp_file.name

    try:
        doc = extractor.extract_pdf(Path(tmp_path))
        return doc, None
    except Exception as e:
        return None, str(e)
    finally:
        os.unlink(tmp_path)

def display_document_summary(doc):
    """Enhanced document summary with discount information"""
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Document Type", doc.metadata.doc_type)
    with col2:
        st.metric("Total Items", len(doc.items))
    with col3:
        st.metric("Total Discount", f"${doc.total_discount:,.2f}")
    with col4:
        st.metric("Grand Total", f"${doc.total:,.2f}")

    if doc.items:
        st.subheader("Line Items")
        items_data = []
        for item in doc.items:
            items_data.append({
                "SKU": item.item_no,
                "Description": item.description,
                "Qty": item.quantity,
                "Unit Price": f"${item.unit_price:.2f}",
                "Discount %": f"{item.discount_pct:.1f}%",
                "Discount Amt": f"${item.discount_amount:.2f}",
                "Total": f"${item.total_price:.2f}"
            })
        st.dataframe(items_data, use_container_width=True)

    st.subheader("Financial Summary")
    fin_col1, fin_col2, fin_col3, fin_col4, fin_col5 = st.columns(5)
    with fin_col1:
        st.metric("Subtotal", f"${doc.subtotal:,.2f}")
    with fin_col2:
        st.metric("Total Discount", f"${doc.total_discount:,.2f}")
    with fin_col3:
        st.metric("Taxable Amount", f"${doc.taxable_amount:,.2f}")
    with fin_col4:
        st.metric("Tax ({:.1f}%)".format(doc.tax_rate), f"${doc.tax:,.2f}")
    with fin_col5:
        st.metric("Grand Total", f"${doc.total:,.2f}")

def handle_pdf_upload():
    st.header("📤 Upload PDF Documents")

    uploaded_files = st.file_uploader(
        "Upload PDF files (PO or Invoice)",
        type="pdf",
        accept_multiple_files=True,
        key="pdf_uploader"
    )

    if uploaded_files:
        col1, col2 = st.columns([1, 1])

        with col1:
            if st.button("📥 Process Documents"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                for idx, pdf_file in enumerate(uploaded_files):
                    status_text.text(f"Processing {pdf_file.name}...")

                    doc, error = extract_pdf_content(pdf_file)

                    if error:
                        st.error(f"Error processing {pdf_file.name}: {error}")
                    else:
                        doc_id = f"doc_{len(st.session_state.uploaded_documents)}"
                        st.session_state.uploaded_documents[doc_id] = {
                            'filename': pdf_file.name,
                            'document': doc,
                            'timestamp': datetime.now().isoformat()
                        }

                        chunk_count = st.session_state.rag_system.add_document(doc, doc_id)
                        st.session_state.extracted_data.append(doc)

                        st.success(f"✓ {pdf_file.name} - {chunk_count} chunks indexed")

                    progress_bar.progress((idx + 1) / len(uploaded_files))

                status_text.text("✓ Processing complete!")

    if st.session_state.uploaded_documents:
        st.subheader("Uploaded Documents")
        for doc_id, doc_info in st.session_state.uploaded_documents.items():
            with st.expander(f"📄 {doc_info['filename']}"):
                display_document_summary(doc_info['document'])

def display_enhanced_comparison_metrics(comparison):
    """Display enhanced comparison metrics with all financial details"""
    st.subheader("📊 Financial Summary")

    metrics = comparison.summary_metrics

    # Create a summary table
    summary_data = {
        'Metric': ['Subtotal', 'Discounts', 'Taxable Amount', 'Tax', 'Grand Total'],
        'Purchase Order': [
            f"${metrics.subtotal_po:,.2f}",
            f"${metrics.discounts_po:,.2f}",
            f"${metrics.taxable_amount_po:,.2f}",
            f"${metrics.tax_po:,.2f}",
            f"${metrics.grand_total_po:,.2f}"
        ],
        'Proforma Invoice': [
            f"${metrics.subtotal_pi:,.2f}",
            f"${metrics.discounts_pi:,.2f}",
            f"${metrics.taxable_amount_pi:,.2f}",
            f"${metrics.tax_pi:,.2f}",
            f"${metrics.grand_total_pi:,.2f}"
        ],
        'Difference': [
            f"${metrics.subtotal_difference:,.2f}",
            f"${metrics.discounts_difference:,.2f}",
            f"${metrics.taxable_difference:,.2f}",
            f"${metrics.tax_difference:,.2f}",
            f"${metrics.grand_total_difference:,.2f}"
        ]
    }

    df = pd.DataFrame(summary_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

def display_item_level_comparison(comparison):
    """Display enhanced item-level comparison with boolean flags"""
    st.subheader("🔍 Item-Level Comparison")

    if not comparison.item_level_comparison:
        st.info("No items to compare. Please check PDF extraction.")
        return

    items_data = []
    for item in comparison.item_level_comparison:
        items_data.append({
            "SKU": item.item_no,
            "Description": item.description,
            "PO Qty": item.po_quantity,
            "Invoice Qty": item.invoice_quantity,
            "Qty Match": "✅" if not item.quantity_discrepancy else "❌",
            "PO Price": f"${item.po_unit_price:.2f}",
            "Invoice Price": f"${item.invoice_unit_price:.2f}",
            "Price Match": "✅" if not item.price_discrepancy else "❌",
            "PO Discount %": f"{item.po_discount_pct:.1f}%",
            "Invoice Discount %": f"{item.invoice_discount_pct:.1f}%",
            "Total Diff": f"${item.total_diff:.2f}",
            "Severity": item.severity,
            "Reason": item.reason
        })

    df = pd.DataFrame(items_data)

    # Color code by severity
    def highlight_severity(row):
        if row['Severity'] == 'CRITICAL':
            return ['background-color: #ffcccc'] * len(row)
        elif row['Severity'] == 'HIGH':
            return ['background-color: #ffffcc'] * len(row)
        elif row['Severity'] == 'MEDIUM':
            return ['background-color: #fff4cc'] * len(row)
        else:
            return [''] * len(row)

    styled_df = df.style.apply(highlight_severity, axis=1)
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

def display_bonus_alerts(comparison):
    """Display bonus alerts generated from comparison"""
    st.subheader("🚨 Automated Alerts & Recommendations")

    # Generate alerts (this should come from report_generator)
    alerts = []

    metrics = comparison.summary_metrics
    total_diff = metrics.grand_total_difference
    variance_pct = abs(total_diff / metrics.grand_total_po * 100) if metrics.grand_total_po > 0 else 0

    if abs(total_diff) > 100 or variance_pct > 3:
        alerts.append({
            "level": "🔴 CRITICAL" if variance_pct > 10 else "🟡 WARNING",
            "message": f"Significant total value discrepancy: PO ${metrics.grand_total_po:,.2f} vs Invoice ${metrics.grand_total_pi:,.2f}. Difference: ${total_diff:,.2f} ({variance_pct:.2f}%)"
        })

    # Item-specific alerts
    critical_items = [item for item in comparison.item_level_comparison if item.severity in ["CRITICAL", "HIGH"]]
    if critical_items:
        for item in critical_items[:5]:  # Show top 5
            if item.price_discrepancy:
                alerts.append({
                    "level": "🟡 WARNING",
                    "message": f"SKU {item.item_no}: Price changed from ${item.po_unit_price:.2f} to ${item.invoice_unit_price:.2f} ({item.reason})"
                })

    # Missing items
    missing_items = [item for item in comparison.item_level_comparison if item.status == "MISSING_FROM_INVOICE"]
    if missing_items:
        alerts.append({
            "level": "🔴 CRITICAL",
            "message": f"{len(missing_items)} item(s) from PO are missing in Invoice"
        })

    if not alerts:
        st.success("✅ No critical alerts. Documents are largely in agreement.")
    else:
        for alert in alerts:
            if "CRITICAL" in alert['level']:
                st.error(f"{alert['level']}: {alert['message']}")
            else:
                st.warning(f"{alert['level']}: {alert['message']}")

def handle_document_comparison():
    if len(st.session_state.extracted_data) >= 2:
        st.header("🔍 Document Comparison & Analysis")

        po_doc = None
        invoice_doc = None

        for doc in st.session_state.extracted_data:
            if 'PURCHASE_ORDER' in doc.metadata.doc_type:
                po_doc = doc
            elif 'PROFORMA_INVOICE' in doc.metadata.doc_type or 'INVOICE' in doc.metadata.doc_type:
                invoice_doc = doc

        if po_doc and invoice_doc:
            if st.button("🔄 Compare Documents", key="compare_btn", type="primary"):
                with st.spinner("Comparing documents..."):
                    comparator = EnhancedDocumentComparator()
                    comparison = comparator.compare(po_doc, invoice_doc)
                    st.session_state.comparison_results = comparison
                    st.session_state.po_doc = po_doc
                    st.session_state.invoice_doc = invoice_doc
                    st.success("✅ Comparison complete!")

            if st.session_state.comparison_results:
                comparison = st.session_state.comparison_results

                # Top-level metrics
                col1, col2, col3, col4, col5 = st.columns(5)
                with col1:
                    st.metric("Total Items", len(comparison.item_level_comparison))
                with col2:
                    st.metric("Matching Items", comparison.matching_items)
                with col3:
                    st.metric("Discrepancies", comparison.discrepant_items)
                with col4:
                    st.metric("Total Variance", f"${comparison.summary_metrics.grand_total_difference:,.2f}")
                with col5:
                    variance_pct = (comparison.summary_metrics.grand_total_difference / comparison.summary_metrics.grand_total_po * 100) if comparison.summary_metrics.grand_total_po != 0 else 0
                    st.metric("Variance %", f"{variance_pct:.2f}%")

                st.divider()

                # Enhanced tabs
                tab_summary, tab_items, tab_alerts, tab_reports = st.tabs([
                    "📊 Financial Summary", 
                    "📋 Item Comparison", 
                    "🚨 Alerts",
                    "📥 Reports"
                ])

                with tab_summary:
                    display_enhanced_comparison_metrics(comparison)

                    st.divider()

                    # Products with mismatches
                    if comparison.products_with_mismatches:
                        st.subheader("⚠️ Products with Mismatches")
                        mismatch_df = pd.DataFrame(comparison.products_with_mismatches)
                        st.dataframe(mismatch_df, use_container_width=True, hide_index=True)

                with tab_items:
                    display_item_level_comparison(comparison)

                with tab_alerts:
                    display_bonus_alerts(comparison)

                with tab_reports:
                    st.subheader("📥 Generate & Download Reports")
                    st.info("Generate comprehensive reports in multiple formats")

                    if st.button("🎯 Generate All Reports", type="primary"):
                        with st.spinner("Generating reports..."):
                            report_paths = generate_all_reports(
                                comparison, 
                                settings.REPORTS_DIR, 
                                po_doc, 
                                invoice_doc
                            )
                            st.success("✅ Reports generated successfully!")

                            # Download buttons
                            col1, col2, col3 = st.columns(3)

                            for idx, (fmt, path) in enumerate(report_paths.items()):
                                with open(path, 'rb') as f:
                                    file_data = f.read()
                                    file_name = Path(path).name

                                    # Determine MIME type
                                    if fmt == 'json':
                                        mime = "application/json"
                                    elif fmt == 'csv':
                                        mime = "text/csv"
                                    elif fmt == 'excel':
                                        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                    else:
                                        mime = "application/octet-stream"

                                    with [col1, col2, col3][idx % 3]:
                                        st.download_button(
                                            label=f"📄 {fmt.upper()}",
                                            data=file_data,
                                            file_name=file_name,
                                            mime=mime,
                                            key=f"download_{fmt}"
                                        )
        else:
            st.warning("⚠️ Please upload both a Purchase Order and an Invoice to compare.")
    else:
        st.info("📤 Please upload at least 2 documents (PO and Invoice) to enable comparison.")

def handle_intelligent_chat():
    st.header("💬 Intelligent Document Chat")

    if not st.session_state.uploaded_documents:
        st.info("Please upload PDF documents first to start chatting.")
        return

    st.subheader("Document Q&A")

    query = st.text_input("Ask a question about your documents:", key="chat_input")

    if query:
        with st.spinner("Searching documents and generating response..."):
            retrieved_results = st.session_state.rag_system.retrieve(query, top_k=5, use_fusion=True)

            context_text = "\n\n".join([r['text'] for r in retrieved_results[:3]])

            result = st.session_state.llm_orchestrator.process_query(query, context_text)

            st.session_state.messages.append({
                "role": "user",
                "content": query,
                "timestamp": datetime.now().isoformat()
            })
            st.session_state.messages.append({
                "role": "assistant",
                "content": result['response'],
                "timestamp": datetime.now().isoformat()
            })

    if st.session_state.messages:
        st.subheader("Conversation History")
        for msg in st.session_state.messages:
            if msg['role'] == 'user':
                st.write(f"**You:** {msg['content']}")
            else:
                st.write(f"**Assistant:** {msg['content']}")

    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

def handle_advanced_analysis():
    st.header("🔬 Advanced Analysis")

    if not st.session_state.comparison_results:
        st.info("Please compare documents first.")
        return

    if st.button("Generate Detailed Analysis"):
        with st.spinner("Analyzing documents..."):
            analysis = st.session_state.llm_orchestrator.analyze_full_comparison(
                {
                    'po_total': st.session_state.comparison_results.summary_metrics.grand_total_po,
                    'invoice_total': st.session_state.comparison_results.summary_metrics.grand_total_pi,
                    'discrepancies': len(st.session_state.comparison_results.item_level_comparison)
                },
                [doc.raw_text[:500] for doc in st.session_state.extracted_data]
            )

            st.subheader("Analysis Report")
            st.write(analysis['report'])

            st.subheader("Document Summary")
            st.write(analysis['summary'])

def main():
    initialize_session()

    st.title("📊 Advanced PDF Analysis & Chat Bot")
    st.markdown("*Extract, Compare, Analyze, and Chat with your PDF documents using Advanced RAG*")

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📤 Upload", "📋 Compare", "💬 Chat", "🔬 Analysis", "📊 Summary"
    ])

    with tab1:
        handle_pdf_upload()

    with tab2:
        handle_document_comparison()

    with tab3:
        handle_intelligent_chat()

    with tab4:
        handle_advanced_analysis()

    with tab5:
        st.header("System Summary")

        rag_summary = st.session_state.rag_system.get_summary()
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Documents Indexed", rag_summary['documents'])
        with col2:
            st.metric("Total Chunks", rag_summary['chunks'])
        with col3:
            st.metric("Retrieval Methods", len(rag_summary['retrieval_methods']))

        st.subheader("Retrieval Methods Available")
        for method in rag_summary['retrieval_methods']:
            st.write(f"✓ {method}")

        st.subheader("Session Info")
        st.write(f"Messages: {len(st.session_state.messages)}")
        st.write(f"Uploaded Documents: {len(st.session_state.uploaded_documents)}")

if __name__ == "__main__":
    main()
