#!/usr/bin/python

import unittest
import datetime
import os
import csv


class Test(unittest.TestCase):
    
    def test(self):
        self.assertEqual(merge(set([("PROJECT", "TASK", "SUBTASK")]), []),
                         [("", "PROJECT", "TASK", "SUBTASK")])

        self.assertEqual(merge(set(), [("tag", "PROJECT", "TASK", "SUBTASK")]),
                         [("#tag", "PROJECT", "TASK", "SUBTASK")])

        self.assertEqual(merge(set([("PROJECT", "TASK", "SUBTASK")]),
                               [("tag ", "PROJECT", "TASK", "SUBTASK")]),
                         [("tag ", "PROJECT", "TASK", "SUBTASK")])


def merge(current_categories, rows):
    current_categories = set(current_categories)
    saved_categories = set()
    tags = dict()
    for tag, project, task, subtask in rows:
        saved_categories.add((project, task, subtask))
        tags[(project, task, subtask)] = tag
    saved_categories.update(current_categories)
    for removed in saved_categories - current_categories:
        tags[removed] = "#%s" % tags[removed] 
    new = []
    for category in saved_categories:
        new.append((tags.get(category, ""),) + category)
    new.sort(key=lambda t: t[1:4])
    return new
 

def get_this_monday():
    now = datetime.datetime.now()
    return now - datetime.timedelta(days=(now.isoweekday() - 1))


IDPREFIX = "FullPage_g_fc03f54b_f4b4_405b_b33f_bba78abceae3__ctl0_"


def get_current_categories():
    from com.gargoylesoftware import htmlunit
    web_client = htmlunit.WebClient(htmlunit.BrowserVersion.FIREFOX_3)
    web_client.getCredentialsProvider().addNTLMCredentials("thill", "Rqdu$4SJ",
        "eportal.cmedresearch.com", 80, "localhost", "MIS")
    web_client.setAjaxController(htmlunit.NicelyResynchronizingAjaxController())

    page = web_client.getPage("http://eportal.cmedresearch.com/Timesheets/mytimesheets.aspx")
    page.getElementById(IDPREFIX + "txtStartDate").setText(get_this_monday().strftime("%d/%b/%Y"))
    page.getFirstByXPath("//input[@value='New']").click()
    page = page.getEnclosingWindow().getEnclosedPage()

    project_dropdown = page.getElementById(IDPREFIX + "ddlProject")

    categories = []
    for project_option in list(project_dropdown.getOptions())[1:]:
        project_dropdown.setSelectedAttribute(project_option, True)
        page = page.getEnclosingWindow().getEnclosedPage()
        task_dropdown = page.getElementById(IDPREFIX + "ddlTask")
        for task_option in list(task_dropdown.getOptions())[1:]:
            task_dropdown.setSelectedAttribute(task_option, True)
            page = page.getEnclosingWindow().getEnclosedPage()
            subtask_dropdown = page.getElementById(IDPREFIX + "ddlSubTask")
            for subtask_option in list(subtask_dropdown.getOptions())[1:]:
                categories.append((project_option.getText(),
                                   task_option.getText(),
                                   subtask_option.getText()))
    page.getFirstByXPath("//input[@value='Delete']").click()
    return categories


def load_current_cataegories():
    rows = []
    try:
        reader = csv.reader(open("timesheet-categories.csv"))
    except IOError:
        pass
    else:
        for row in reader:
            if len(row) == 3:
                rows.append(tuple(row))
    return rows


def main():
    
    filepath = os.path.expanduser("~/.timesheet-categories.csv")
    rows = []
    try:
        reader = csv.reader(open(filepath))
    except IOError:
        pass
    else:
        for row in reader:
            if len(row) == 4:
                rows.append(row)
    rows = merge(load_current_cataegories(), rows)
    writer = csv.writer(open(filepath, "w"))
    for row in rows:
        writer.writerow(row)


if __name__ == "__main__":
#    unittest.main()
    main()

