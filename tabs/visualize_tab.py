"""
Tab for uploading and visualizing E1000 data
Save as: tabs/visualize_tab.py
"""
import pandas as pd
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QStackedWidget, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class VisualizeTab(QWidget):
    """Tab for uploading existing E1000 results and viewing visualizations"""

    def __init__(self, data_store):
        super().__init__()
        self.data_store = data_store
        self.df = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # ── Title ────────────────────────────────────────────────────────────
        title = QLabel("Visualise current E1000 data")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)

        info1 = QLabel("If you have already downloaded the current E1000 results, you can look at the results here.")
        info1.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info1)

        info2 = QLabel("Upload the results excel file from 'Get current E1000 data'.")
        info2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info2)

        # ── Upload button ─────────────────────────────────────────────────────
        self.upload_results_btn = QPushButton("📁 Upload E1000 results (Excel / CSV)")
        self.upload_results_btn.clicked.connect(self.upload_results_file)
        self.upload_results_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 2px dashed #999;
                border-radius: 8px;
                padding: 20px;
                font-size: 14px;
                color: #333;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
                border-color: #1E40AF;
                color: #1E40AF;
            }
            QPushButton:pressed { background-color: #d8d8d8; }
        """)
        self.upload_results_btn.setMinimumHeight(60)
        layout.addWidget(self.upload_results_btn)

        self.upload_status = QLabel("")
        self.upload_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.upload_status)

        # ── Report-type selector (hidden until file loaded) ───────────────────
        self.report_selector_frame = QFrame()
        self.report_selector_frame.setVisible(False)
        rs_layout = QHBoxLayout(self.report_selector_frame)
        rs_layout.setContentsMargins(0, 0, 0, 0)

        rs_label = QLabel("Report type:")
        rs_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        rs_layout.addWidget(rs_label)

        self.report_combo = QComboBox()
        self.report_combo.addItems(["Regular Report", "End-of-Year (EOY) Report"])
        self.report_combo.setStyleSheet("font-size: 13px; padding: 4px 8px;")
        self.report_combo.currentIndexChanged.connect(self.switch_report)
        rs_layout.addWidget(self.report_combo)
        rs_layout.addStretch()

        layout.addWidget(self.report_selector_frame)

        # ── Stacked widget: page 0 = Regular, page 1 = EOY ───────────────────
        self.stack = QStackedWidget()
        self.stack.setVisible(False)
        layout.addWidget(self.stack)

        # Page 0 – Regular report
        self.regular_page = QWidget()
        self._build_regular_page()
        self.stack.addWidget(self.regular_page)

        # Page 1 – EOY report
        self.eoy_page = QWidget()
        self._build_eoy_page()
        self.stack.addWidget(self.eoy_page)

        layout.addStretch()

    # ──────────────────────────────────────────────────────────────────────────
    # Page builders
    # ──────────────────────────────────────────────────────────────────────────

    def _build_regular_page(self):
        layout = QVBoxLayout(self.regular_page)
        layout.setSpacing(10)

        # Sex filter
        filter_row = QHBoxLayout()
        filter_label = QLabel("Filter by Sex:")
        filter_label.setStyleSheet("font-weight: bold;")
        filter_row.addWidget(filter_label)

        self.sex_combo = QComboBox()
        self.sex_combo.addItems(["All", "F", "M"])
        self.sex_combo.setStyleSheet("font-size: 13px; padding: 4px 8px;")
        self.sex_combo.currentIndexChanged.connect(self.refresh_regular_report)
        filter_row.addWidget(self.sex_combo)
        filter_row.addStretch()
        layout.addLayout(filter_row)

        # Leaderboard table
        self.leaderboard_table = QTableWidget()
        self.leaderboard_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.leaderboard_table.setAlternatingRowColors(True)
        self.leaderboard_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.leaderboard_table.setMinimumHeight(250)
        layout.addWidget(self.leaderboard_table)

        # Chart
        self.regular_figure = Figure(figsize=(6, 3), tight_layout=True)
        self.regular_canvas = FigureCanvas(self.regular_figure)
        self.regular_canvas.setMinimumHeight(250)
        layout.addWidget(self.regular_canvas)

    def _build_eoy_page(self):
        layout = QVBoxLayout(self.eoy_page)
        layout.setSpacing(10)

        eoy_title = QLabel("End-of-Year Report")
        eoy_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        eoy_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(eoy_title)

        # Summary stats table
        self.eoy_table = QTableWidget()
        self.eoy_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.eoy_table.setAlternatingRowColors(True)
        self.eoy_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.eoy_table.setMinimumHeight(250)
        layout.addWidget(self.eoy_table)

        # EOY chart
        self.eoy_figure = Figure(figsize=(6, 3), tight_layout=True)
        self.eoy_canvas = FigureCanvas(self.eoy_figure)
        self.eoy_canvas.setMinimumHeight(250)
        layout.addWidget(self.eoy_canvas)

    # ──────────────────────────────────────────────────────────────────────────
    # File upload
    # ──────────────────────────────────────────────────────────────────────────

    def upload_results_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Results File", "",
            "Excel Files (*.xlsx *.xls);;CSV Files (*.csv)")

        if not file_path:
            return

        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            required_cols = ['Name', 'Point']
            missing_cols = [c for c in required_cols if c not in df.columns]
            if missing_cols:
                QMessageBox.warning(self, "Warning",
                    f"Missing expected columns: {', '.join(missing_cols)}\n\n"
                    "This might not be an E1000 results file.")

            self.df = df
            self.data_store.set_results_data(df)

            self.upload_status.setText(
                f"✓ Loaded {len(df)} results from {file_path.split('/')[-1]}")
            self.upload_status.setStyleSheet(
                "color: green; font-weight: bold; font-size: 14px;")

            # Show report controls
            self.report_selector_frame.setVisible(True)
            self.stack.setVisible(True)
            self.switch_report(self.report_combo.currentIndex())

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file: {str(e)}")
            self.upload_status.setText("❌ Failed to load file")
            self.upload_status.setStyleSheet("color: red; font-weight: bold;")

    # ──────────────────────────────────────────────────────────────────────────
    # Report switching
    # ──────────────────────────────────────────────────────────────────────────

    def switch_report(self, index):
        self.stack.setCurrentIndex(index)
        if index == 0:
            self.refresh_regular_report()
        else:
            self.refresh_eoy_report()

    # ──────────────────────────────────────────────────────────────────────────
    # Regular report
    # ──────────────────────────────────────────────────────────────────────────

    def refresh_regular_report(self):
        if self.df is None:
            return

        df = self.df.copy()

        # Sex filter
        sex_filter = self.sex_combo.currentText()
        if sex_filter != "All" and 'Sex' in df.columns:
            df = df[df['Sex'] == sex_filter]

        # Aggregate points per swimmer
        grouped = (
            df.groupby('Name', as_index=False)['Point']
            .sum()
            .sort_values('Point', ascending=False)
            .reset_index(drop=True)
        )
        grouped.insert(0, 'Place', grouped.index + 1)

        # ── Table ──
        cols = list(grouped.columns)
        self.leaderboard_table.setRowCount(len(grouped))
        self.leaderboard_table.setColumnCount(len(cols))
        self.leaderboard_table.setHorizontalHeaderLabels(cols)

        for row_idx, row in grouped.iterrows():
            for col_idx, col in enumerate(cols):
                item = QTableWidgetItem(str(row[col]))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                # Gold / silver / bronze highlight
                if col == 'Place':
                    if row['Place'] == 1:
                        item.setBackground(QColor("#FFD700"))
                    elif row['Place'] == 2:
                        item.setBackground(QColor("#C0C0C0"))
                    elif row['Place'] == 3:
                        item.setBackground(QColor("#CD7F32"))
                self.leaderboard_table.setItem(row_idx, col_idx, item)

        # ── Bar chart (top 15) ──
        top = grouped.head(15)
        self.regular_figure.clear()
        ax = self.regular_figure.add_subplot(111)

        colors = []
        for place in top['Place']:
            if place == 1:
                colors.append('#FFD700')
            elif place == 2:
                colors.append('#C0C0C0')
            elif place == 3:
                colors.append('#CD7F32')
            else:
                colors.append('#1E40AF')

        ax.barh(top['Name'][::-1], top['Point'][::-1], color=colors[::-1])
        ax.set_xlabel('Total Points')
        title_suffix = f" ({sex_filter})" if sex_filter != "All" else ""
        ax.set_title(f"Leaderboard – Top {len(top)}{title_suffix}")
        ax.tick_params(axis='y', labelsize=8)
        self.regular_canvas.draw()

    # ──────────────────────────────────────────────────────────────────────────
    # EOY report
    # ──────────────────────────────────────────────────────────────────────────

    def refresh_eoy_report(self):
        if self.df is None:
            return

        df = self.df.copy()

        grouped = df.groupby('Name', as_index=False)['Point'].sum()
        total_points = grouped['Point'].sum()
        avg_points = grouped['Point'].mean()
        num_swimmers = len(grouped)

        # Per-swimmer stats
        swimmer_stats = (
            grouped
            .assign(
                Average=grouped['Point'],   # each swimmer already summed; rename for clarity
            )
            .rename(columns={'Point': 'Total Points'})
            .sort_values('Total Points', ascending=False)
            .reset_index(drop=True)
        )
        swimmer_stats.insert(0, 'Rank', swimmer_stats.index + 1)

        # ── Table ──
        cols = list(swimmer_stats.columns)
        self.eoy_table.setRowCount(len(swimmer_stats))
        self.eoy_table.setColumnCount(len(cols))
        self.eoy_table.setHorizontalHeaderLabels(cols)

        for row_idx, row in swimmer_stats.iterrows():
            for col_idx, col in enumerate(cols):
                val = row[col]
                if col == 'Total Points':
                    text = f"{val:.1f}"
                elif col == 'Average':
                    text = f"{val:.2f}"
                else:
                    text = str(val)
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.eoy_table.setItem(row_idx, col_idx, item)

        # ── Summary bar at top ──
        # Re-use first row as a summary header by inserting a row
        self.eoy_table.insertRow(0)
        summary_data = {
            'Rank': '—',
            'Name': f"TOTAL: {total_points:.0f} pts  |  AVG/swimmer: {avg_points:.1f} pts  |  Swimmers: {num_swimmers}",
            'Total Points': '',
            'Average': '',
        }
        for col_idx, col in enumerate(cols):
            item = QTableWidgetItem(summary_data.get(col, ''))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setBackground(QColor("#1E40AF"))
            item.setForeground(QColor("#FFFFFF"))
            font = QFont()
            font.setBold(True)
            item.setFont(font)
            self.eoy_table.setItem(0, col_idx, item)

        # ── Chart: total points per swimmer (top 20) ──
        top = swimmer_stats.head(20)
        self.eoy_figure.clear()
        ax = self.eoy_figure.add_subplot(111)
        bars = ax.bar(top['Name'], top['Total Points'], color='#1E40AF', alpha=0.85)
        ax.axhline(avg_points, color='red', linestyle='--', linewidth=1.5,
                   label=f"Avg: {avg_points:.1f}")
        ax.set_ylabel('Total Points')
        ax.set_title('EOY – Total Points per Swimmer (Top 20)')
        ax.legend()
        ax.tick_params(axis='x', rotation=45, labelsize=7)
        self.eoy_figure.tight_layout()
        self.eoy_canvas.draw()