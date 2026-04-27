
Fine Policy:
  Week 1  (Day  1–7 ) : ₹10/day/book
  Week 2  (Day  8–14) : ₹20/day/book   (10 × 2)
  Week 3  (Day 15–21) : ₹60/day/book   (10 × 2 × 3)
  Week 4  (Day 22–28) : ₹240/day/book  (10 × 2 × 3 × 4)
  ... continues multiplying each week
"""
from datetime import datetime, timedelta
def fine_rate_for_day(overdue_day: int) -> int:
    """Return fine rate (₹/day) for a given overdue day number (1-indexed)."""
    week = (overdue_day - 1) // 7 + 1   # which week this day falls in
    rate = 10
    for w in range(1, week):
        rate *= (w + 1)
    return rate


def calculate_fine(overdue_days: int) -> int:
    """Calculate total fine for given number of overdue days."""
    if overdue_days <= 0:
        return 0
    total = 0
    for day in range(1, overdue_days + 1):
        total += fine_rate_for_day(day)
    return total

class Book:
    def __init__(self, book_id: str, title: str, author: str, genre: str = "General"):
        self.book_id   = book_id
        self.title     = title
        self.author    = author
        self.genre     = genre
        self.available = True

    def __str__(self):
        status = "✅ Available" if self.available else "🔴 Issued"
        return (f"  [{self.book_id}] {self.title}\n"
                f"       Author : {self.author}\n"
                f"       Genre  : {self.genre}\n"
                f"       Status : {status}")

class IssueRecord:
    _counter = 1

    def __init__(self, book_id, student_name, student_id,
                 issue_date: datetime, issue_days: int, phone: str = "N/A"):
        self.record_id    = f"R{IssueRecord._counter:04d}"
        IssueRecord._counter += 1
        self.book_id      = book_id
        self.student_name = student_name
        self.student_id   = student_id
        self.phone        = phone
        self.issue_date   = issue_date
        self.issue_days   = issue_days
        self.due_date     = issue_date + timedelta(days=issue_days)
        self.return_date  = None
        self.fine_paid    = 0
        self.status       = "Issued"

    def days_overdue(self, return_date: datetime) -> int:
        delta = (return_date - self.due_date).days
        return max(0, delta)

    def __str__(self):
        info = (f"  Record ID    : {self.record_id}\n"
                f"  Book ID      : {self.book_id}\n"
                f"  Student      : {self.student_name} ({self.student_id})\n"
                f"  Phone        : {self.phone}\n"
                f"  Issue Date   : {self.issue_date.strftime('%d-%m-%Y')}\n"
                f"  Due Date     : {self.due_date.strftime('%d-%m-%Y')}\n"
                f"  Status       : {self.status}")
        if self.return_date:
            info += f"\n  Return Date  : {self.return_date.strftime('%d-%m-%Y')}"
        if self.fine_paid > 0:
            info += f"\n  Fine Paid    : ₹{self.fine_paid}"
        return info

class Library:
    def __init__(self, name: str = "City Central Library"):
        self.name    = name
        self.books   = {}    # book_id  → Book
        self.records = {}    # record_id → IssueRecord
        self._seed_books()

    def _seed_books(self):
        """Pre-load a few demo books."""
        defaults = [
            ("B001", "Introduction to Python", "Eric Matthes",   "Programming"),
            ("B002", "The Alchemist",           "Paulo Coelho",   "Fiction"),
            ("B003", "Clean Code",              "Robert C. Martin","Programming"),
            ("B004", "Wings of Fire",           "A.P.J. Abdul Kalam","Biography"),
        ]
        for bid, title, author, genre in defaults:
            self.books[bid] = Book(bid, title, author, genre)

    def _divider(self, char="─", width=58):
        print(char * width)

    def _header(self, text: str):
        self._divider("═")
        print(f"  {text}")
        self._divider("═")

    def _parse_date(self, prompt: str) -> datetime:
        while True:
            raw = input(prompt).strip()
            if raw == "":
                return datetime.today()
            try:
                return datetime.strptime(raw, "%d-%m-%Y")
            except ValueError:
                print("  ⚠️  Invalid format. Use DD-MM-YYYY (leave blank for today).")


    def add_book(self):
        self._header("ADD NEW BOOK")
        book_id = input("  Enter Book ID      : ").strip().upper()
        if not book_id:
            print("  ❌ Book ID cannot be empty."); return
        if book_id in self.books:
            print(f"  ❌ Book ID '{book_id}' already exists."); return

        title  = input("  Enter Title        : ").strip()
        author = input("  Enter Author       : ").strip()
        genre  = input("  Enter Genre        : ").strip() or "General"

        if not title or not author:
            print("  ❌ Title and Author are required."); return

        self.books[book_id] = Book(book_id, title, author, genre)
        print(f"\n  ✅ Book '{title}' added successfully!")

    def view_books(self):
        self._header(f"ALL BOOKS — {self.name}")
        if not self.books:
            print("  No books in the library yet."); return
        avail  = [b for b in self.books.values() if b.available]
        issued = [b for b in self.books.values() if not b.available]
        print(f"  Total: {len(self.books)}  |  Available: {len(avail)}  |  Issued: {len(issued)}\n")
        self._divider()
        for book in self.books.values():
            print(book)
            self._divider()

    def search_book(self):
        self._header("SEARCH BOOK")
        query = input("  Search by title / author / ID : ").strip().lower()
        results = [b for b in self.books.values()
                   if query in b.title.lower()
                   or query in b.author.lower()
                   or query in b.book_id.lower()]
        if not results:
            print("  🔍 No matching books found."); return
        print(f"  Found {len(results)} result(s):\n")
        for b in results:
            print(b); self._divider()

    # ── ISSUE BOOK ────────────────────────────

    def issue_book(self):
        self._header("ISSUE BOOK")
        available = {bid: b for bid, b in self.books.items() if b.available}
        if not available:
            print("  ❌ No books are currently available."); return

        print("  Available Books:")
        for bid, b in available.items():
            print(f"    [{bid}] {b.title} — {b.author}")
        self._divider()

        book_id = input("  Enter Book ID to issue : ").strip().upper()
        if book_id not in available:
            print("  ❌ Invalid Book ID or book not available."); return

        student_name = input("  Student Full Name      : ").strip()
        student_id   = input("  Student ID / Roll No.  : ").strip()
        phone        = input("  Contact Number         : ").strip() or "N/A"

        if not student_name or not student_id:
            print("  ❌ Student name and ID are required."); return

        issue_date = self._parse_date("  Issue Date (DD-MM-YYYY, blank=today) : ")

        while True:
            try:
                days = int(input("  Issue for how many days? (1–28) : "))
                if 1 <= days <= 28:
                    break
                print("    Please enter between 1 and 28 days.")
            except ValueError:
                print("   Enter a valid number.")

        record = IssueRecord(book_id, student_name, student_id,
                             issue_date, days, phone)
        self.records[record.record_id] = record
        self.books[book_id].available  = False

        due_str = record.due_date.strftime("%d-%m-%Y")
        self._divider("═")
        print(f"   Book Issued Successfully!")
        print(f"    Title     : {self.books[book_id].title}")
        print(f"    Student   : {student_name} ({student_id})")
        print(f"   Issue Date: {issue_date.strftime('%d-%m-%Y')}")
        print(f"   Due Date  : {due_str}")
        self._divider()
        print("    FINE NOTICE (if returned after due date):")
        print("     Week 1 (Day  1–7 ) : ₹10/day/book")
        print("     Week 2 (Day  8–14) : ₹20/day/book")
        print("     Week 3 (Day 15–21) : ₹60/day/book")
        print("     Week 4 (Day 22–28) : ₹240/day/book")
        print(f"    Record ID : {record.record_id}")
        self._divider("═")

    def return_book(self):
        self._header("RETURN BOOK")
        active = {rid: r for rid, r in self.records.items() if r.status == "Issued"}
        if not active:
            print("  ℹ No books are currently issued."); return

        print("  Currently Issued Books:")
        for rid, r in active.items():
            title = self.books.get(r.book_id, Book(r.book_id,"?","?")).title
            print(f"    [{rid}] {title}  →  {r.student_name}  (due {r.due_date.strftime('%d-%m-%Y')})")
        self._divider()

        record_id = input("  Enter Record ID to process return : ").strip().upper()
        if record_id not in active:
            print("   Invalid Record ID."); return

        record = active[record_id]
        return_date = self._parse_date("  Return Date (DD-MM-YYYY, blank=today) : ")

        overdue_days = record.days_overdue(return_date)
        fine         = calculate_fine(overdue_days)

        record.return_date = return_date
        record.fine_paid   = fine
        record.status      = "Returned"
        self.books[record.book_id].available = True

        book_title = self.books[record.book_id].title
        self._divider("═")
        print(f"    Book Returned : {book_title}")
        print(f"    Student       : {record.student_name} ({record.student_id})")
        print(f"   Due Date      : {record.due_date.strftime('%d-%m-%Y')}")
        print(f"    Return Date   : {return_date.strftime('%d-%m-%Y')}")
        self._divider()
        if overdue_days == 0:
            print("   Returned on time — No fine applicable. Thank you!")
        else:
            print(f"    Overdue by    : {overdue_days} day(s)")
            print(f"    Fine Charged  : ₹{fine}")
            print(f"\n  Fine Breakdown (per day):")
            for day in range(1, overdue_days + 1):
                rate = fine_rate_for_day(day)
                print(f"    Day {day:>2} : ₹{rate}")
            print(f"           Total : ₹{fine}")
        self._divider("═")

    def view_records(self):
        self._header("ALL ISSUE RECORDS")
        if not self.records:
            print("  No records found."); return
        today = datetime.today()
        for rid, r in self.records.items():
            print(r)
            if r.status == "Issued":
                od = r.days_overdue(today)
                if od > 0:
                    est = calculate_fine(od)
                    print(f"   Currently {od} day(s) overdue — estimated fine: ₹{est}")
            self._divider()

    def show_fine_chart(self):
        self._header("FINE STRUCTURE CHART")
        print("  Days Overdue   Rate (₹/day)   Week")
        self._divider()
        for day in range(1, 29):
            rate = fine_rate_for_day(day)
            week = (day - 1) // 7 + 1
            bar = "█" * min(rate // 10, 30)
            print(f"  Day {day:>2}  :  ₹{rate:<6}  Week {week}  {bar}")
        self._divider()
        print("  Pattern: 10 → 20 → 60 → 240 → ... (×week number each week)")


    def menu(self):
        options = {
            "1": ("Add New Book",       self.add_book),
            "2": ("View All Books",     self.view_books),
            "3": ("Search Book",        self.search_book),
            "4": ("Issue a Book",       self.issue_book),
            "5": ("Return a Book",      self.return_book),
            "6": ("View All Records",   self.view_records),
            "7": ("Fine Structure Chart", self.show_fine_chart),
            "0": ("Exit",               None),
        }
        print("\n" + "═" * 58)
        print(f"   Welcome to {self.name}")
        print("═" * 58)
        while True:
            print("\n  ┌─ MAIN MENU ──────────────────┐")
            for key, (label, _) in options.items():
                print(f"  │  [{key}] {label:<28}│")
            print("  └──────────────────────────────┘")
            choice = input("\n  Enter your choice : ").strip()
            if choice == "0":
                print("\n   Thank you for using the Library System. Goodbye!\n")
                break
            elif choice in options:
                print()
                options[choice][1]()
            else:
                print("   Invalid option. Please try again.")
if __name__ == "__main__":
    lib = Library("City Central Library")
    lib.menu()