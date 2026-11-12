# Name Surname - NIU XXXXXXX
# Name Surname - NIU XXXXXXX

import os


def Read_Text_File(filename):
    try:
        f = open(filename, "r", encoding="utf-8")
    except:
        raise FileNotFoundError
    try:
        text = f.read()
    except UnicodeDecodeError:
        f.close()
        f = open(filename, "r", encoding="windows-1252")
        text = f.read()
    f.close()
    return text


def DocClass_Welcome():
    print("Document Classification is typically used in Document Processing for")
    print("assigning categories to documents. Thus, it eases their posterior")
    print("processing and analysis.")
    print()
    print("The program “DocumentClassification” classifies an input folder")
    print("containing documents in txt format. It will also receive a file")
    print("containing information about the topics to classify.")
    print()
    print("The program will generate the following files:")
    print("A txt file containing the category of the documents")
    print("A txt file containing the statistics of the classification")


def Read_Categories_Keywords(filename):
    l_categories = []
    l_keywords = []
    text = Read_Text_File(filename)
    for line in text.split("\n"):
        if ":" in line:
            parts = line.split(":")
            l_name = parts[0].split()
            if len(l_name) > 0:
                l_categories.append(l_name[0].lower())
                l_keywords.append(set(parts[1].lower().split()))
    return l_categories, l_keywords


def Document_Reader(filename):
    text = Read_Text_File(filename)
    clean = ""
    for c in text:
        if c.isalnum():
            clean = clean + c.lower()
        else:
            clean = clean + " "
    l_words = clean.split()
    return l_words


def Count_Frequencies(l_words, l_categories, l_keywords):
    d_frequencies = {}
    for i in range(len(l_categories)):
        d_frequencies[l_categories[i]] = {}
        for keyword in l_keywords[i]:
            d_frequencies[l_categories[i]][keyword] = 0
    for word in l_words:
        for i in range(len(l_categories)):
            if word in l_keywords[i]:
                d_frequencies[l_categories[i]][word] += 1
    return d_frequencies


def Classify_Doc(d_frequencies):
    d_totals = {}
    total_all = 0
    for category in d_frequencies:
        total_occurrences = 0
        for keyword in d_frequencies[category]:
            total_occurrences += d_frequencies[category][keyword]
        d_totals[category] = total_occurrences
        total_all += total_occurrences
    d_votes = {}
    doc_category = "UNKNOWN"
    for category in d_totals:
        if total_all > 0:
            exact_percentage = d_totals[category] * 100 / total_all
        else:
            exact_percentage = 0
        d_votes[category] = (d_totals[category], round(exact_percentage))
        if exact_percentage > 50:
            doc_category = category
    return d_votes, doc_category


def Is_Txt(file_name):
    return file_name[-4:].lower() == ".txt"


def Folder_Has_Txt(folder_name):
    found = False
    if os.path.isdir(folder_name):
        l_files = os.listdir(folder_name)
        i = 0
        while i < len(l_files) and not found:
            if Is_Txt(l_files[i]) and os.path.isfile(os.path.join(folder_name, l_files[i])):
                found = True
            else:
                i += 1
    return found


def Line_Of_Document(file_name, d_votes, doc_category, d_frequencies):
    l_parts = []
    for category in d_votes:
        l_parts.append(category + ":" + str(d_votes[category][1]) + "%")
    line = file_name + ": " + doc_category + "(" + ", ".join(l_parts) + ")"
    if doc_category != "UNKNOWN":
        l_counts = []
        l_names = []
        for keyword in d_frequencies[doc_category]:
            l_names.append(keyword)
        l_names.sort()
        for keyword in l_names:
            l_counts.append(keyword + ":" + str(d_frequencies[doc_category][keyword]))
        line = line + ": " + ", ".join(l_counts)
    return line


if __name__ == "__main__":
    DocClass_Welcome()

    l_categories = []
    while len(l_categories) == 0:
        keywords_file = input("Enter the name of the keywords file: ")
        try:
            l_categories, l_keywords = Read_Categories_Keywords(keywords_file)
            if len(l_categories) == 0:
                print("Error: the file contains no data.")
        except FileNotFoundError:
            print("Error: the file does not exist.")

    folder_name = input("Enter the name of the folder with the documents: ")
    while not Folder_Has_Txt(folder_name):
        print("Error: the folder does not exist or contains no txt files.")
        folder_name = input("Enter the name of the folder with the documents: ")
    base_name = folder_name
    if base_name[-1] == "/" or base_name[-1] == "\\":
        base_name = base_name[:-1]

    total_txt = 0
    d_category_docs = {}
    for category in l_categories + ["UNKNOWN"]:
        d_category_docs[category] = 0
    d_keyword_totals = {}
    for keywords in l_keywords:
        for keyword in keywords:
            d_keyword_totals[keyword] = 0

    out = open(base_name + "_DocClassification.txt", "w", encoding="utf-8")
    for file_name in sorted(os.listdir(folder_name)):
        file_path = os.path.join(folder_name, file_name)
        if os.path.isfile(file_path):
            if Is_Txt(file_name):
                try:
                    l_words = Document_Reader(file_path)
                    d_frequencies = Count_Frequencies(l_words, l_categories, l_keywords)
                    d_votes, doc_category = Classify_Doc(d_frequencies)
                except FileNotFoundError:
                    print("Error: the file", file_name, "could not be read.")
                else:
                    out.write(Line_Of_Document(file_name, d_votes, doc_category, d_frequencies) + "\n")
                    total_txt += 1
                    d_category_docs[doc_category] += 1
                    d_doc_keywords = {}
                    for category in d_frequencies:
                        for keyword in d_frequencies[category]:
                            d_doc_keywords[keyword] = d_frequencies[category][keyword]
                    for keyword in d_doc_keywords:
                        d_keyword_totals[keyword] += d_doc_keywords[keyword]
            else:
                out.write("Attention: the following non txt file has been detected: " + file_name + "\n")
    out.close()

    stats = open(base_name + "_DCStatistics.txt", "w", encoding="utf-8")
    stats.write("*** Statistics\n")
    stats.write("Total txt files: " + str(total_txt) + "\n")
    for category in l_categories + ["UNKNOWN"]:
        if total_txt > 0:
            percentage = d_category_docs[category] * 100 / total_txt
        else:
            percentage = 0
        stats.write(category + ": " + "{0:.2f}".format(percentage) + "%\n")
    stats.write("\n*** Top 10 keywords\n")
    l_names = []
    for keyword in d_keyword_totals:
        l_names.append(keyword)
    l_names.sort()
    l_counts = []
    for keyword in l_names:
        l_counts.append(d_keyword_totals[keyword])
    k = 0
    while k < 10 and len(l_names) > 0:
        pos = 0
        for i in range(1, len(l_counts)):
            if l_counts[i] > l_counts[pos]:
                pos = i
        stats.write(l_names[pos] + ": " + str(l_counts[pos]) + "\n")
        del l_names[pos]
        del l_counts[pos]
        k += 1
    stats.close()
