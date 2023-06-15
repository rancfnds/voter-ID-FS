from flask import Flask, render_template, request
import csv

app = Flask(__name__)

class BPlusTree:
    def __init__(self, file):
        self.index_file = file
        self.key_to_pointer = {}
        self.loadIndex()

    def loadIndex(self):
        try:
            with open(self.index_file, 'r') as file:
                reader = csv.reader(file)
                for row in reader:
                    key, pointer = row
                    self.key_to_pointer[key] = int(pointer)
        except FileNotFoundError:
            print("Index file not found. Creating a new index.")

    def saveIndex(self):
        try:
            with open(self.index_file, 'w') as file:
                writer = csv.writer(file)
                for key, pointer in self.key_to_pointer.items():
                    writer.writerow([key, pointer])
        except IOError:
            print("Error saving index.")

    def insert(self, key, pointer):
        self.key_to_pointer[key] = pointer

    def remove(self, key):
        del self.key_to_pointer[key]

    def display(self):
        records = []
        for key, pointer in self.key_to_pointer.items():
            records.append({"key": key, "pointer": pointer})
        return records


def displayAllRecords():
    try:
        with open("voter_records.txt", 'r') as file:
            reader = csv.reader(file)
            records = []
            for row in reader:
                id, name, age = row
                records.append({"id": id, "name": name, "age": age})
            return records
    except FileNotFoundError:
        print("Unable to open file!")


def addRecord(tree, id, name, age):
    try:
        with open("voter_records.txt", 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([id, name, age])
            tree.insert(id, file.tell())
            tree.saveIndex()
            return True
    except IOError:
        return False


def searchRecord(search_term):
    try:
        with open("voter_records.txt", 'r') as file:
            reader = csv.reader(file)
            records = []
            for row in reader:
                id, name, age = row
                if id == search_term or name == search_term:
                    records.append({"id": id, "name": name, "age": age})
            return records
    except FileNotFoundError:
        print("Unable to open file!")


def deleteRecord(tree, search_term):
    try:
        with open("voter_records.txt", 'r') as file:
            reader = csv.reader(file)
            records = []
            found = False
            for row in reader:
                id, name, age = row
                if id == search_term or name == search_term:
                    found = True
                else:
                    records.append(row)
        if found:
            with open("voter_records.txt", 'w', newline='') as outFile:
                writer = csv.writer(outFile)
                writer.writerows(records)
            tree.remove(search_term)
            tree.saveIndex()
            return True
        else:
            return False
    except FileNotFoundError:
        print("Unable to open file!")


def updateRecord(tree, search_term, new_id, new_name, new_age):
    try:
        with open("voter_records.txt", 'r+') as file:
            records = []
            found = False
            for row in csv.reader(file):
                id, name, age = row
                if id == search_term or name == search_term:
                    found = True
                    row = [new_id, new_name, new_age]
                records.append(row)
            if found:
                file.seek(0)
                file.truncate()
                writer = csv.writer(file)
                writer.writerows(records)
                tree.remove(search_term)
                file.seek(0, 2)
                tree.insert(new_id, file.tell())
                tree.saveIndex()
                return True
            else:
                return False
    except FileNotFoundError:
        print("Unable to open file!")


def bPlusTreeDisplay(tree):
    return tree.display()


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        if 'display_all' in request.form:
            records = displayAllRecords()
            return render_template('index.html', records=records)
        elif 'add_record' in request.form:
            id = request.form['id']
            name = request.form['name']
            age = request.form['age']
            success = addRecord(bplusTree, id, name, age)
            if success:
                message = "Record added successfully!"
            else:
                message = "Failed to add record."
            return render_template('index.html', message=message)
        elif 'search_record' in request.form:
            search_term = request.form['search_term']
            records = searchRecord(search_term)
            return render_template('index.html', records=records)
        elif 'delete_record' in request.form:
            search_term = request.form['search_term']
            success = deleteRecord(bplusTree, search_term)
            if success:
                message = "Record deleted successfully!"
            else:
                message = "Record not found!"
            return render_template('index.html', message=message)
        elif 'update_record' in request.form:
            search_term = request.form['search_term']
            new_id = request.form['new_id']
            new_name = request.form['new_name']
            new_age = request.form['new_age']
            success = updateRecord(bplusTree, search_term, new_id, new_name, new_age)
            if success:
                message = "Record updated successfully!"
            else:
                message = "Record not found!"
            return render_template('index.html', message=message)
        elif 'display_tree' in request.form:
            tree = bPlusTreeDisplay(bplusTree)
            return render_template('index.html', tree=tree)
    return render_template('index.html')


if __name__ == "__main__":
    bplusTree = BPlusTree("bplus_index.txt")
    app.run(debug=True)
