
import sys
import pickle


IDPREFIX = "FullPage_g_fc03f54b_f4b4_405b_b33f_bba78abceae3__ctl0_"


def get_page(username, password):
    from com.gargoylesoftware import htmlunit
    import java
#    java.lang.System.setProperty("org.apache.commons.logging.Log", "org.apache.commons.logging.impl.SimpleLog");
#    java.lang.System.setProperty("org.apache.commons.logging.simplelog.showdatetime", "true");
#    java.lang.System.setProperty("org.apache.commons.logging.simplelog.defaultlog", "debug");

    web_client = htmlunit.WebClient(htmlunit.BrowserVersion.FIREFOX_3)
    web_client.getCredentialsProvider().addNTLMCredentials(username, password,
        "eportal.cmedresearch.com", 80, "localhost", "MIS")
    web_client.setAjaxController(htmlunit.NicelyResynchronizingAjaxController())
    return web_client.getPage("http://eportal.cmedresearch.com/Timesheets/mytimesheets.aspx")


def upload_timesheet(username, password, monday_date, entries):
    page = get_page(username, password)
    page.getElementById(IDPREFIX + "txtStartDate").setText(monday_date.strftime("%d/%b/%Y"))
    page = page.getFirstByXPath("//input[@value='New']").click()
    for (project, task, subtask), times in entries:
        print (project, task, subtask), times
        
        project_dropdown = page.getElementById(IDPREFIX + "ddlProject")
        page = project_dropdown.setSelectedAttribute(project, True)
        task_dropdown = page.getElementById(IDPREFIX + "ddlTask")
        page = task_dropdown.setSelectedAttribute(task, True)
        subtask_dropdown = page.getElementById(IDPREFIX + "ddlSubTask")
        page = subtask_dropdown.setSelectedAttribute(subtask, True)
        for day, time in zip(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
                             times):
            input = page.getElementById(IDPREFIX + "txt%s" % day)
            input.focus() # need to set focus as input uses onblur event
            if time != 0:
                input.setText(str(time))
#        print page.asText()
        add_entry_button = page.getElementById(IDPREFIX + "btnAddEntry")
        add_entry_button.focus()
        page = add_entry_button.click()
        #print repr(page.asXml())
    page = page.getFirstByXPath("//input[@value='Submit']").click()


def main():
    pickle_path = sys.argv[1]
    upload_timesheet(*pickle.load(open(pickle_path)))
    

if __name__ == "__main__":
    main()

