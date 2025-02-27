import csv
import logging
import os

log_file_name = "RESULT.log"
logging.basicConfig(filename=log_file_name, level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class CSVFileManager:
    def read_csv(self, file_path):
        try:
            data = []
            with open(file_path, 'r') as file:
                start_reading = False
                # Look for the header row
                for row in file:
                    if 'Name' in row:
                        start_reading = True
                        headers = [header.strip() for header in row.split(',')]
                        break

                if start_reading:
                    # Read data into a list of dictionaries
                    reader = csv.DictReader(file, fieldnames=headers)
                    for row in reader:
                        data.append(row)

            logging.debug(f"Read {len(data)} rows from {file_path}")
            return data

        except FileNotFoundError as e:
            logging.error(f"File not found: {file_path}")
            raise e

    def write_csv(self, file_path, headers, data, output_file_exists):
        try:
            with open(file_path, 'w', newline='') as file:
                # Write data to the CSV file
                writer = csv.writer(file)
                writer.writerow(headers)
                for row in data:
                    cleaned_row = [value if value is not None and value != [''] else '' for value in row.values()]
                    writer.writerow(cleaned_row)
            logging.debug(f"Data written to {file_path}")
            if output_file_exists:
                self.remove_existing_output_file(file_path)
        except Exception as e:
            logging.error(f"Error writing to CSV file {file_path}: {str(e)}")
            raise e

    def remove_existing_output_file(self, output_file_path):
        try:
            if os.path.exists(output_file_path):
                os.remove(output_file_path)
                logging.debug(f"Removed existing output file: {output_file_path}")
        except Exception as e:
            logging.error(f"Error removing existing output file: {str(e)}")


class AttendanceTracker:
    def update_attendance(self, day_data):
        try:
            global present_set
            # Update the set of present attendees using only email for comparison
            present_set = {add['Email'].lower() for add in day_data if 'Email' in add}
            return present_set
        except Exception as e:
            logging.error(f"Error updating attendance: {str(e)}")
            raise e

    def calculate_attendance_percentage(self, add, total_days, day_files):
        try:
            # Calculate attendance percentage for an individual
            present_days = sum(add[day_key] == 'Present' for day_key in day_files)
            attendance_percentage = (present_days / total_days) * 100 if total_days > 0 else 0
            add['Attendance Percentage'] = f"{attendance_percentage:.2f}%"
            logging.debug(f"Attendance percentage for {add['Name']}: {attendance_percentage:.2f}%")
            return round(attendance_percentage, 2)
        except Exception as e:
            logging.error(f"Error calculating attendance percentage: {str(e)}")
            raise e


class AttendanceDataPresenter:
    def display_data(self, formatted_headers, main_data, day_files, attendance_dict):
        try:
            for add in main_data:
                total_days = len(day_files)
                AttendanceTracker().calculate_attendance_percentage(add, total_days,[day_file.replace('.csv', '') for day_file in day_files])
        except Exception as e:
            logging.error(f"Error displaying data: {str(e)}")
            raise e


class AttendanceManager:
    def main(self):
        try:
            # Collect necessary information from the user
            folder_path = input("Enter the folder path containing day files and main file: ")
            output_file_name = input("Enter the output file name (without extension):")
            excluded_files = ['totalmembers.csv', f"{output_file_name}.csv"]
            day_files = [file for file in os.listdir(folder_path) if
                         file not in excluded_files]

            output_file_path = os.path.join(os.path.dirname(folder_path), f"{output_file_name}.csv")
            output_file_exists = os.path.exists(output_file_path)

            # Create objects for each class
            csv_manager = CSVFileManager()
            attendance_tracker = AttendanceTracker()
            data_presenter = AttendanceDataPresenter()

            # Read main data from the CSV file
            main_data = csv_manager.read_csv(os.path.join(folder_path, "totalmembers.csv"))

            if not main_data:
                logging.error("Main file is empty.")
                return  # Exit the program if the main file is empty.

            # Initialize a dictionary to track attendance for each day
            attendance_dict = {day_file.replace('.csv', ''): {'Present': 0, 'Absent': 0} for day_file in day_files}

            # Process attendance for each day
            for day_file_path in day_files:
                logging.debug(f"Processing day file: {day_file_path}")

                # Reset attendance information in main_data for each day
                for add in main_data:
                    day_key = day_file_path.replace('.csv', '')
                    add[day_key] = 'Not Marked'

                # Read data from the day file
                day_data = csv_manager.read_csv(os.path.join(folder_path, day_file_path))

                # Check for the 'Name' and 'Email' headers in day_data
                if 'Name' not in day_data[0] or 'Email' not in day_data[0]:
                    logging.error(f"'Name' or 'Email' header is missing in {day_file_path}")
                    return  # Exit the program if the 'Name' or 'Email' header is missing.

                day_key = day_file_path.replace('.csv', '')
                attendance_tracker.update_attendance(day_data)

                # Update attendance and track counts using only email for comparison
                for add in main_data:
                    key = add['Email'].lower()  # Convert to lowercase for comparison
                    if key in {email.lower() for email in present_set}:
                        add[day_key] = 'Present'
                        attendance_dict[day_key]['Present'] += 1
                    else:
                        add[day_key] = 'Absent'
                        attendance_dict[day_key]['Absent'] += 1

                # Check for attendees not in the main data using only email for comparison
                for add in present_set:
                    if add not in {person['Email'].lower() for person in main_data}:
                        logging.warning(f"Email {add} attended but is not part of {day_file_path}")

            # Display individual attendance details
            data_presenter.display_data(main_data[0].keys(), main_data, day_files, attendance_dict)

            # Display the summary like count of absent and present
            logging.info("Summary Report:")
            for status, count in attendance_dict.items():
                logging.info(f"{status}: {count['Present']} Present, {count['Absent']} Absent")

            # Write the updated main file with attendance information
            if output_file_name and not output_file_exists:
                columns_to_write = ['Name', 'Email'] + day_files + ['Attendance Percentage']
                csv_manager.write_csv(output_file_path, columns_to_write, main_data, output_file_exists)
                logging.info(f"Attendance information written to {output_file_path}")
            elif not output_file_name:
                logging.warning("Output file name not provided. Attendance info not written to any file.")
            elif output_file_exists:
                logging.warning(
                    f"Output file {output_file_path} already exists. Attendance info not written to any file.")

            logging.info("Program executed successfully")

        except Exception as e:
            logging.error(f"Unhandled error in the program execution: {str(e)}", exc_info=True)
            raise e  # Reraise the exception for visibility.

if __name__ == '__main__':
    attendance_manager = AttendanceManager()
    attendance_manager.main()
