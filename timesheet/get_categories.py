
import datetime
import os
import csv


def get_this_monday():
    now = datetime.datetime.now()
    return now - datetime.timedelta(days=(now.isoweekday() - 1))


IDPREFIX = "FullPage_g_fc03f54b_f4b4_405b_b33f_bba78abceae3__ctl0_"


def get_page(username, password):
    from com.gargoylesoftware import htmlunit
    web_client = htmlunit.WebClient(htmlunit.BrowserVersion.FIREFOX_3)
    web_client.getCredentialsProvider().addNTLMCredentials(username, password,
        "eportal.cmedresearch.com", 80, "localhost", "MIS")
    web_client.setAjaxController(htmlunit.NicelyResynchronizingAjaxController())
    return web_client.getPage("http://eportal.cmedresearch.com/Timesheets/mytimesheets.aspx")


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


def main():
    rows = get_current_categories()
    writer = csv.writer(open("timesheet-categories.csv", "w"))
    for row in rows:
        writer.writerow(row)


if __name__ == "__main__":
    main()