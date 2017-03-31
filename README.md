# Whatscorp

Whatscorp is simple script that parses whatsapp chat backups and turns them into something more useful for corpus linguistics analysis. I will post documentation at a later point, in the meantime feel free
to contact me if you have questions.

## Requirements

- Python 3.x
- The dateutil module (see requirements.txt)

## Usage

1) Place any number of chat log textfiles into the "import" folder
2) (Optional) Modify "settings.xml" with an editor (see __Settings__ below)
3) Run whatscorp.py to create XML versions for each 

In addition to XML files, the next version of Whatscorp will also create CSV versions
of the corpus files.

## Settings
If <split> is set to 1, Whatscorp will create a separate file for each user in a chat.

If <scramble> is set to 1 it will convert the usernames into something less 
identifyable. Please note that this is a simple hash and can be reversed. It does not
provide true anonymity. Whatscorp also only scrambles the names at the start of a message, not any
named mentions within the text.


```xml
<settings>
    <split>0</split>
    <scramble log="1">1</scramble>
</settings> 

```

In a future update, setting the log attribute of <scramble> to 1 will create a file that
lists the unscrambled and scrambled strings for all users in a chat.

