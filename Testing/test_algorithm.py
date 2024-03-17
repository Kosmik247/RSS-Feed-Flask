from website.external_functions import valid_email


def test_regex():

    # Regex emails 
    email_pass = "Bob@gmail.com"
    email_fail = "Bob@gm"

    test_1 = valid_email(email_pass)
    assert test_1 == True
    test_2 = valid_email(email_fail)
    assert test_2 == False
