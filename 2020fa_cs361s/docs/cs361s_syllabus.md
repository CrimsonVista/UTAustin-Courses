# UT-Austin CS 361S - Network Security and Privacy

|||
|---|---|
| Instructor: | Seth James Nielson (sethjn@cs.utexas.edu) |
| TA: | Serdjan Rolovic |
| Class Times: | Mondays/Wednesdays at 2pm |
| Location: | Virtual-Zoom |
| Slack: | fall2020utcs361s.slack.com |
| Professor Office Hours | Immediately after class and by appointment |
| TA Office Hours | ?? |

# Covid-19 and Virtual Instruction

This class is being taught in a completely online fashion. Every effort
is being made to insure high quality of instruction, lab-work, and
collaboration. If you have any feedback, including criticism or
suggestions, please feel free to reach out.

# Overview

In this course, we will learn about core concepts that are crucial 
in modern network security and privacy. Unfortunately, these concepts are 
so broad that we will only be scratching the surface of a *subset* of 
available sub-topics, principles, and applications. The goal, however, is 
that the foundational experience gained here will permit students to 
continue learning about Network Security and Privacy either in later classes, 
in their careers, or through independent learning.

# University-mandated Disclosures

## Safety and Class Participation/Masks
We will all need to make some adjustments in order to benefit from 
in-person classroom interactions in a safe and healthy manner. Our best 
protections against spreading COVID-19 on campus are masks (defined as cloth 
face coverings) and staying home if you are showing symptoms. Therefore, 
for the benefit of everyone, this is means that all students are required 
to follow these important rules. 

1. Every student must wear a cloth face-covering properly in class and in 
all campus buildings at all times. 
1. Students are encouraged to participate in documented daily symptom screening.  
This means that each class day in which on-campus activities occur, students must 
upload certification from the symptom tracking app and confirm that they completed 
their symptom screening for that day to Canvas.  Students should not 
upload the results of that screening, just the certificate that they completed it. 
If the symptom tracking app recommends that the student isolate rather than 
coming to class, then students must not return to class until cleared by a medical professional.
1. Information regarding [safety protocols with and without symptoms](https://healthyhorns.utexas.edu/coronavirus_exposure_action_chart.html) 
can be [found here](https://healthyhorns.utexas.edu/coronavirus_exposure_action_chart.html).

If a student is not wearing a cloth face-covering properly in the classroom (or any UT building), that student must leave the classroom (and building). If the student refuses to wear a cloth face covering, class will be dismissed for the remainder of the period, and the student will be subject to disciplinary action as set forth in the university’s Institutional Rules/General Conduct 11-404(a)(3). Students who have a condition that precludes the wearing of a cloth face covering must follow the procedures for obtaining an accommodation working with Services for Students with Disabilities.

## Sharing of Course Materials is Prohibited
No materials used in this class, including, but not limited to, lecture hand-outs, 
videos, assessments (quizzes, exams, papers, projects, homework assignments), 
in-class materials, review sheets, and additional problem sets, may be shared online 
or with anyone outside of the class unless you have my explicit, written permission. 
Unauthorized sharing of materials promotes cheating. It is a violation of the 
University’s Student Honor Code and an act of academic dishonesty. I am well aware 
of the sites used for sharing materials, and any materials found online that are 
associated with you, or any suspected unauthorized sharing of materials, will be 
reported to Student Conduct and Academic Integrity in the Office of the Dean of 
Students. These reports can result in sanctions, including failure in the course. 

## Class Recordings
Class recordings are reserved only for students in this class for educational purposes 
and are protected under FERPA. The recordings should not be shared outside the class 
in any form. Violation of this restriction by a student could lead to Student 
Misconduct proceedings.

## COVID Caveats
To help keep everyone at UT and in our community safe, it is critical that 
students report COVID-19 symptoms and testing, regardless of test results, to 
University Health Services, and faculty and staff report to the HealthPoint Occupational 
Health Program (OHP) as soon as possible. Please see this link to understand what 
needs to be reported.  In addition, to help understand what to do if a fellow student 
in the class (or the instructor or TA) tests positive for COVID, see this 
[University Health Services link](https://healthyhorns.utexas.edu/coronavirus_exposure_action_chart.html).

# Expectations

## Pre-requisites

The formal prerequisite for CS 361S is CS 439 (or 352 or 372) or 
CS 439H (or 352H or 372H). This prerequisite will be strictly enforced.
If you wish to be added, we have been instructed to refer you to the
*Computer Science* counseling office.

In addition to the course pre-requisites, the labwork for this
course will make use of a variety of tools and technologies 
including:

1. C programming
1. Python programming
1. Some assembly programming
1. Linux command-line tools and system administration (e.g., apt, deb, rpm, etc)
1. Virtual Machines, such as VirtualBox
1. Debugging tools (e.g., gdb)
1. Git

There is also a special framework that the professor has developed to
enable remote and in-person students to interface their networking programs
together.

You do not need to be an expert with these tools but you will be expected to
come up to speed for the assignments.

## Major Course Goals

This course is roughly divided into two modules:

1. Constructive: what security and privacy properties are, why they matter, 
and how they are enforced.
1. Destructive: the concepts, including theoretical concepts, behind computer 
security failures, why they are difficult to overcome, and how attackers use
these to bypass the enforcement mechanisms used in the Modern Internet

As an introductory course, there is an immense amount of breadth required.
It should comeas no surprise that the labwork cannot possibly cover all
of this breadth. We will be using a textbook this semester to expose you
to security and privacy principles.

*MAJOR DISCLAIMER:* The professor does NOT like the book. It has out-of-date
information, overly simplistic explantions, and a host of other probles. There is not,
as yet, a good Network Security and Privacy book available (in the Professor's opinion).
This book was chosen because it touches on a reasonably wide range of principles
in a reasonably sufficient depth of technical discussion. We will use the book
as a starting point for learning, but that is all.

### Constructive Concepts

By the end of the course, students are expected to understand the basic concepts
behind constructing a secure network and ensuring privacy. The concepts we will
focus on in class are:

1. What are security properties such as confidentiality, integrity, and authenticity?
1. What are some basic concepts of enforcing security properties such as authentication and authorization?
1. What is the role of cryptography in enforcing security properties?
1. What is the role of secure protocols in enforcing security properties?
1. What is the role of monitoring traffic in enforcing security properties?

### Destructive Concepts

By the end of the course, students are expected to understand the basic concepts
behind failures in network security and privacy technologies that result in the
destruction (violation) of intended security policies. The concepts we will focus
on in class are:

1. What is a vulnerability, what is an exploit, and what is a compromise of a securty property?
1. How does computer science theory, such as the Halting Problem, impact the nature of failures?
1. What are software vulnerabilities, such as buffer overflow vulnerabilities?
1. What are cryptographic vulnerabilities?
1. What are protocol and application vulnerabilities, such as web and database vulnerabilities?
1. What principles of secure design can help in mitigating vulnerabilities, exploits, and compromises?
1. What is the role of intrusion detection in mitigating vulnerabilities, exploits, and compromises?

# Course Policies

## Subject-to-Change
This is the instructor's second semester teaching this course. Some
portions of this syllabus, including labs, are copied from
a previous semester. Please
pay attention for updates, as any number of items may
need to change throughout the semester.

## Attendance

COVID-19 NOTE: Attendance applies as much as possible to virtual
learners. We would like the class to be together (virtually)
during class time. The goal is to ask questions, have discussions,
and learn together.

Attending lectures and keeping up with the readings is crucial 
for success in CS 361S.

You must not register for another class whose lecture times 
overlap those of CS 361S, even in part. You must not register 
for a class section whose time overlaps with those of CS 361S, even in part.

## Office Hours
Your instructor is an adjunct faculty; that means he is not on campus
regularly and does not have an office. However, the professor will generally
be available after class for discussions on Zoom. And, especially in 
the middle of a pandemic, is available for virtual meetings.

Your TA will hold regular office hours, listed on the course 
home page. 

Office hours are the best way to get extended help with the course material. 
Please come to office hours!

## Ethics and Ethical "Hacking"
You cannot learn about computer security without learning how computer security
is bypassed, broken, or otherwise "hacked." This means that you will be more
capable of *harming* people in order to be able to know how to *defend* them
better. We will even have some exercises in this class that simulate or
re-create compromising a system.

By attending this course, you are agreeing to be ethical in the use of this
information. You should not, under any circumstances, use this course as
an excuse to harm other people or violate security systems. You are responsible
for knowing what is and is not acceptable use of any of the systems you will
use this semester. If you have any questions, you are welcome to ask the professor.

## Textbook and Readings
The textbook for this course, terrible though it may be, is "Guide to
Computer Network Security" 5th edition by Kizza.

We will occasionally make reference to the following books that 
are freely available online:

1. [Ross Anderson, Security Engineering 2nd ed.](https://www.cl.cam.ac.uk/~rja14/book.html)
1. [Handbook of Applied Cryptography](http://cacr.uwaterloo.ca/hac/)

We will also use additional papers for certain topics. These will be distributed 
later.

You are REQUIRED as part of the course to read assigned sections of the textbook,
additional references, and assigned paper.

To evaluate your reading, you are required to schedule a time period to meet IN A CHAT
ROOM (via Slack or Zoom) with a group of other students on a weekly basis. Your meetings will last
approximately 20 minutes and involve no more than five students. You will either send
a transcript of the chat to the TA (if chatting via Zoom) or invite the TA to the slack channel.
You will be scored
based on your participation in the 20-minute discussion.

Your score is NOT dependent on UNDERSTANDING the material. Your score is dependent on
having read the material and efforts made to understand it. For example, if you read
something that you didn't understand, your score during the discussion might be based
on the insightful questions that you ask your peers or references to other online
sources (even Wikipedia) that you used to try and get a better grasp of the concept.

The TA will not participate or offer additional insights/corrections/feedback. The TA
will only be attending to grade the discussion. However, the TA may bring questions
or struggles from these groups to the professor's attention in order for the professor
to address these questions in class.

You need to have your meeting during the following week after the assigned reading.
There are 14 weeks, so there will be 13 group meetings/discussions (we will not 
require you to meet to discuss the last week's readings).

If you struggle to participate in groups like this for any reason (English is your second
language, social anxiety, time pressure, etc.), please contact the professor to work
out a solution.

## Programming Projects and Written Homework
There will be six programming assignments.

You will need to get a github account and create a private repo
for this course. You need to invite the TA and the professor
to join the repo, so you will need a "professional" github
account. You can get this for free by registering for the GitHub
Student Pack. Please ask if you can't figure this out.

Once you have your account, you need to create a repository
for your submissions. Please send the professor and the TA
an email with your github name and your github repository.

Source code for the course will also be made available in
a class github repository. Details will be provided in individual
lab write-ups.

Different labs will permit different levels of collaboration.
Please make sure that you understand what is and is not
permitted for each lab and ask if you have any questions.

## Exams

There will be two midterm exams. The professor
is still figuring out how to test the remote students and more
information will be forthcoming.

The exams will be exclusively ESSAY QUESTIONS, but will have
no restrictions related to refering to the book, notes, or
even the Internet. The only restriction will be that you may
not talk to another human being (classmates, roommates, etc).
The exam will also be strictly timed. There will be a hard
deadline for submission after which there will be immediate
deductions in grades, so it is ideal to try to finish the
exam early and submit early in order to ensure that transission
delays and other issues don't cause you to lose points.

The scoring for exam will NOT focus on your writing skills, grammar,
spelling, etc. Instead, each question will require you to 
build explanations, arguments, or narratives based around technical
concepts you have learned. We will score your essay on the 
correct application of these technical concepts to the question. See
this [list](list_of_concepts.md) for technical concepts you might draw on for an 
essay response

Any indication of cheating, such as copying another students
answers, collaborating with another student, communicating with
another human about the test questions, etc. will result in an
automatic 0 on the exam and a full grade deduction (A to B, B+ to C+, etc.).

## Grading

* Labs are strictly Pass/Fail. 10% each (60%)
* Reading discussions (10%)
* Exams. 15% each. (30%)
* 2 Possible extra credit projects.
* Cheating is an automatic fail of the assignment and a full grade deduction.

Because labs are pass fail, we will provide various mechanisms
for verifying that your lab is correct before submission, such
as an auto-grader. We will be autograding all assignments.

Given the pass/fail nature of projects, you may resubmit with
no penalty any time before the due date. That is, you may 
submit, receive a score, and then re-submit any time before the 
due date for a new auto-score.

You may request, exactly once, a regrade of a programming project within two
days of receiving your score. You request will be granted 
so long as it is clear that you had a functional project and you are not
simply using this as a two-week extension. The professor has the final
say as to whether the regrade is allowed.

In order to make life reasonable on the TA's who will be grading
your submissions, you must complete all labwork within five
school days of the due date. Each date late is a 20% penalty.

# Calendar

||||
|---|---|---|
| Date | Lecture | Assignments |
| WEEK 1 |
| 8/26 | REMOTE LECTURE: Introduction to Network Security | Reading 1.1: KIZZA 2.1-2.3, ANDERSON 1 |
| 8/31 | LECTURE: Ross Anderson's "Security Policies" | DUE: Reading 1.1 |
| | | Reading 1.2: KIZZA 9 |
| WEEK 2 |
| 9/2 | LECTURE: Access controls and Authorization | DUE: Reading 1.2 |
| | | Reading 2.1: KIZZA 10 |
| | | Lab 1: Authentication and Authorization Lab |
| 9/7 | Holiday |
| 9/9 | LECTURE: AUTHORIZATION | DUE: Reading 2.1 |
| | | Reading 2.2: KIZZA 5.1, 5.2 |
| WEEK 3 |
| 9/14 | LECTURE: Introduction to Cryptography | DUE: Reading 2.2 |
| | | Reading 3.1: ANDERSON 11.1, 11.2, 11.7 |
| 9/16 | LECTURE: Symmetric Cryptography | DUE: Reading 3.1 |
| | | Reading 3.2: KIZZA 11.3, 11.4, 11.8 |
| WEEK 4 |
| 9/21 | LECTURE: Asymmetric Cryptography | DUE: Reading 3.2, Lab 1 |
| | | Reading 4.1: KIZZA 11.5, 11.6, TLS 1.2 RFC 5246 |
| | | Lab 2: TLS-Protected Communications |
| 9/23 | LECTURE: PKI, Certificates, and TLS | DUE: Reading 4.1 |
| | | Reading 4.2: ANDERSON 3.1-3.3.1 |
| WEEK 5 |
| 9/28 | LECTURE: Network Security Protocols | DUE: Reading 4.2 |
| | | Reading 5.1: KIZZA 17 |
| 9/30 | LECTURE: IPSec, Kerberos | DUE: Reading  5.1 |
| | | Reading 5.2: KIZZA 12 |
| WEEK 6 |
| 10/5 | LECTURE: Firewalls | DUE: Reading 5.2, Lab 2 |
| | | Reading 6.1: [Day in the Life of a Packet](https://knowledgebase.paloaltonetworks.com/KCSArticleDetail?id=kA10g000000ClVHCA0) |
| | | Lab 3: Firewall Lab |
| 10/7 | LECTURE: Advanced Firewalls | DUE: Reading 6.1 |
| | | Reading 6.2: KIZZA 4 |
| WEEK 7 |
| 10/12 | REVIEW and EXAM PREP | |
| 10/14 | EXAM 1 | |
| WEEK 8 | 
| 10/19 | LECTURE: Introduction to Vulnerabilities | DUE: Reading 6.2, Lab 3 |
| | | Reading 8.1: [Buffer Overflow](https://www.cs.utexas.edu/~shmat/courses/cs380s_fall09/cowan.pdf) |
| | | Lab 4: Buffer Overflow and Return Oriented Programming | 
| 10/21 | LECTURE: Buffer Overflows. Why is this so hard? | DUE: Reading 8.1 |
| | | Reading 8.2: KIZZA 15, [Cohen's 1987 Virus Paper](https://www.profsandhu.com/cs5323_s18/cohen-1987.pdf) |
| WEEK 9 |
| 10/26 | LECTURE: Viruses and the Halting Problem | DUE: Reading 8.2 |
| | | Reading 9.1: ANDERSON 21.3 |
| 10/28 | LECTURE: Malware | DUE: Reading 9.1 |
| | | Reading 9.2: TBA | 
| WEEK 10 |
| 11/2 | LECTURE: Sample cryptography attacks on block ciphers | DUE: Reading 9.2, Lab 4 |
| | | Reading 10.1: TBA |
| | | Lab 5: TLS Interception |
| 11/4 | LECTURE: The trust problem and PKI | DUE: Reading 10.1 |
| | | Reading 10.2: ANDERSON 21.2.1 |
| WEEK 11 |
| 11/9 | LECTURE: Classic Network Attacks - Syn Flood, DDOS, DNS Spoofing  | DUE: Reading 10.2 |
| | | Reading 11.1: ANDERSON 3.3.2-3.5 |
| 11/11 | LECTURE: Protocol Attacks - MITM, Chosen Protocol Attacks | DUE: Reading 11.1 |
| | | Reading 11.2: KIZZA 13.1-13.5 |
| WEEK 12 |
| 11/16 | LECTURE: Itrusion Detection | DUE: Reading 11.2, Lab 5 |
| | | Reading 12.1: KIZZA 13.6-13.11 |
| | | Lab 6: TBA |
| 11/18 | LECTURE: Intrusion Prevention, Honeypots | DUE: Reading 12.1 | 
| | | Reading 12.2: KIZZA 21.3-21.5|
| WEEK 13 |
| 11/23| LECTURE: Sandboxing and Virtualization | DUE: Reading 12.2 |
| | | Reading 13.1: KIZZA 21.6, Formal Verification Paper TBA |
| 11/25 | Holiday |
| 11/30 | LECTURE: Formal Verification |
| WEEK 14 |
| 12/2 | Review and Exam Prep | DUE: Lab 6 |
| 12/7 | EXAM 2 | |

# Labs
Coming Soon

# Additional Resources
coming Soon
