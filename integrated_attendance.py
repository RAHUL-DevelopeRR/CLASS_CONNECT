#!/usr/bin/env python3
"""
INTEGRATED ATTENDANCE SYSTEM
Combines all attendance functionality into a single, clean solution
"""

import pandas as pd
import sqlite3
import random
import os
import json
from datetime import datetime, timedelta

def generate_attendance_data():
    """Generate sample attendance data with actual CSBS students and dynamic dates"""

    # Actual CSBS students with roll numbers and names
    csbs_students = [
        ('927623BCB001', 'ABINAYA'),
        ('927623BCB002', 'ANITHA MARY'),
        ('927623BCB003', 'ARUTHRA KANAGARAJ'),
        ('927623BCB004', 'BARANI'),
        ('927623BCB005', 'DEEPIKA'),
        ('927623BCB006', 'DEVISREE'),
        ('927623BCB007', 'DHARANEESH KESAVAN'),
        ('927623BCB008', 'DHARANI'),
        ('927623BCB009', 'DHARSNI'),
        ('927623BCB010', 'GOKUL'),
        ('927623BCB011', 'HARISH'),
        ('927623BCB012', 'INDHUJA'),
        ('927623BCB013', 'JAGANNATH'),
        ('927623BCB014', 'JANNATHUL FIRTHOS'),
        ('927623BCB015', 'KABILESH'),
        ('927623BCB016', 'KALPANA'),
        ('927623BCB017', 'KANISH'),
        ('927623BCB018', 'KARUNYA'),
        ('927623BCB019', 'KAVIPRIYA'),
        ('927623BCB020', 'KIRTHICK'),
        ('927623BCB021', 'KRISHNAKANTH'),
        ('927623BCB022', 'KUMARAVEL'),
        ('927623BCB023', 'LAKSHMI'),
        ('927623BCB024', 'LATHIKA'),
        ('927623BCB025', 'MADHUPRIYA'),
        ('927623BCB026', 'MAITHILI'),
        ('927623BCB027', 'MANIKANDAN'),
        ('927623BCB028', 'MATHIVANAN'),
        ('927623BCB029', 'MONEESH'),
        ('927623BCB030', 'MUKUNDBALAJI'),
        ('927623BCB031', 'NARMADHA'),
        ('927623BCB032', 'PAVITHRA'),
        ('927623BCB033', 'PRAHADEESH'),
        ('927623BCB034', 'PRASANNA KUMAR'),
        ('927623BCB035', 'PRAVIN KUMAR'),
        ('927623BCB036', 'PRIYADHARSHINI'),
        ('927623BCB037', 'RAHUL'),
        ('927623BCB038', 'RAKSHITHA'),
        ('927623BCB039', 'RENGANATHAN'),
        ('927623BCB040', 'RISHANTH'),
        ('927623BCB041', 'SAHANAA'),
        ('927623BCB042', 'SANJAY SARUNATH'),
        ('927623BCB043', 'SARAVANAN'),
        ('927623BCB044', 'SHALINI'),
        ('927623BCB045', 'SIBIDHARAN'),
        ('927623BCB046', 'SRIDEVI'),
        ('927623BCB047', 'SUBALAKSHMI SRIDHAR'),
        ('927623BCB048', 'SUBHIKSHA'),
        ('927623BCB049', 'SUDHARSAN'),
        ('927623BCB050', 'SUDHARSANA KUMAR'),
        ('927623BCB051', 'SUGANYA'),
        ('927623BCB052', 'THARANI'),
        ('927623BCB053', 'THIRUSELVAM'),
        ('927623BCB054', 'VARSAA VIHASINI'),
        ('927623BCB055', 'VARUN KARTHICK'),
        ('927623BCB056', 'VIGNESH'),
        ('927623BCB057', 'VISVA PRIYA'),
        ('927623BCB058', 'YASVANTH PALANI'),
        ('927623BCB059', 'ABINAYA'),
        ('927623BCB060', 'ANITHA MARY'),
    ]

    # Generate dynamic dates - last 60 working days (excluding weekends)
    dates = []
    current_date = datetime.now()
    days_added = 0
    while days_added < 60:
        # Skip weekends (Saturday=5, Sunday=6)
        if current_date.weekday() < 5:
            # Format: d-Mon-yy (e.g., 17-Jan-26)
            dates.append(current_date.strftime('%-d-%b-%y') if os.name != 'nt' else current_date.strftime('%#d-%b-%y'))
            days_added += 1
        current_date -= timedelta(days=1)
    
    # Reverse to get chronological order (oldest first)
    dates.reverse()

    # Create attendance data
    attendance_data = []

    for i, (rollno, name) in enumerate(csbs_students, 1):
        row = {'S. No.': i, 'ROLL NO': rollno, 'NAME': name, 'BRANCH': 'CSBS'}

        # Generate attendance for each date (80% present, 20% absent)
        for date in dates:
            if random.random() < 0.8:  # 80% chance of present
                row[date] = 'P'
            else:
                row[date] = 'A'

        attendance_data.append(row)

    return attendance_data, dates

def create_attendance_excel():
    """Create Excel file with attendance data"""

    print("📊 Generating attendance data...")

    attendance_data, dates = generate_attendance_data()

    # Create DataFrame
    df = pd.DataFrame(attendance_data)

    # Save to Excel
    excel_file = 'attendance.xlsx'
    df.to_excel(excel_file, index=False)

    print(f"✅ Created {excel_file} with {len(attendance_data)} CSBS students")
    print(f"✅ {len(dates)} attendance dates generated")
    print(f"✅ Total attendance records: {len(attendance_data) * len(dates)}")

    return excel_file

def load_attendance_to_database():
    """Load attendance data from generated Excel file to database"""

    excel_file = 'attendance.xlsx'

    if not os.path.exists(excel_file):
        print(f"❌ Excel file not found: {excel_file}")
        return False

    try:
        # Read Excel file
        df = pd.read_excel(excel_file)
        print(f"✅ Read Excel file: {len(df)} rows, {len(df.columns)} columns")

        # Find roll number column
        rollno_col = None
        for col in df.columns:
            if 'ROLL' in str(col).upper():
                rollno_col = col
                print(f"✅ Found roll number column: {col}")
                break

        if rollno_col is None:
            print("❌ No roll number column found")
            return False

        # Connect to database
        conn = sqlite3.connect('school.db')
        cursor = conn.cursor()

        # Clear existing attendance
        cursor.execute('DELETE FROM attendance')
        print("✅ Cleared existing attendance data")

        # Insert attendance data
        inserted_count = 0
        csbs_count = 0

        for _, row in df.iterrows():
            rollno = str(row[rollno_col]).strip()
            if not rollno:
                continue

            is_csbs = 'BCB' in rollno.upper() or rollno.startswith('927623')

            # Insert for each date column
            for col in df.columns:
                if col not in ['S. No.', rollno_col] and pd.notna(row[col]):
                    date_val = str(row[col]).strip()
                    if date_val:
                        status = str(row[col]).strip().upper()
                        if status in ['P', 'PRESENT', '1', 'YES', 'Y']:
                            status = 'P'
                        elif status in ['A', 'ABSENT', '0', 'NO', 'N']:
                            status = 'A'

                        cursor.execute('INSERT INTO attendance (rollno, date, status) VALUES (?, ?, ?)',
                                     (rollno, str(col), status))
                        inserted_count += 1
                        if is_csbs:
                            csbs_count += 1

        conn.commit()
        conn.close()

        print(f"✅ Successfully inserted {inserted_count} attendance records")
        print(f"✅ CSBS attendance records: {csbs_count}")

        # Verify
        conn = sqlite3.connect('school.db')
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM attendance')
        total = cursor.fetchone()[0]
        print(f"✅ Total attendance records in database: {total}")

        cursor.execute('SELECT COUNT(*) FROM attendance WHERE rollno LIKE "%BCB%" OR rollno LIKE "927623%"')
        csbs_total = cursor.fetchone()[0]
        print(f"✅ CSBS attendance records: {csbs_total}")

        # Show sample
        cursor.execute('SELECT rollno, date, status FROM attendance WHERE rollno LIKE "%BCB%" OR rollno LIKE "927623%" LIMIT 5')
        samples = cursor.fetchall()
        print("\n📊 Sample CSBS attendance:")
        for sample in samples:
            print(f"  {sample[0]} - {sample[1]}: {sample[2]}")

        conn.close()

        print("\n🎉 SUCCESS! Attendance data loaded to database!")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function to run the integrated attendance system"""

    print("🔧 INTEGRATED ATTENDANCE SYSTEM")
    print("=" * 50)

    # Create Excel file
    excel_file = create_attendance_excel()

    # Load to database
    if load_attendance_to_database():
        print("\n🎉 Attendance sync completed successfully!")
        print("You can now:")
        print("1. Run your Flask app: python app.py")
        print("2. Check attendance in admin dashboard")
        print("3. View CSBS student attendance percentages")
    else:
        print("\n❌ Attendance sync failed")
        print("Please check the error messages above")

if __name__ == "__main__":
    main()
