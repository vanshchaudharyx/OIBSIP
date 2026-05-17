Secure Password Generator
A Python project that generates strong, random passwords using the command line (CLI) and a graphical interface (GUI).<br>
About the Project<br>
This project helps users create secure passwords based on their preferences like length and character types (uppercase, lowercase, numbers, <br>symbols). It has two modes — a simple CLI for beginners and a full GUI for advanced users.<br>


How to Run<br>
Launch GUI:<br>
python main.py<br>


Launch CLI:<br>
python main.py --cli<br>
CLI with options:<br>
python cli.py --length 16 --count 3<br>
python cli.py --no-symbols<br>
python cli.py --quiet<br>



Features<br>
Cryptographically secure using Python's secrets module<br>
Password strength meter (Very Weak to Very Strong)<br>
Clipboard copy with one click<br>
Password history (last 50 passwords)<br>
Works on Windows, macOS, and Linux<br>
No external libraries required<br>