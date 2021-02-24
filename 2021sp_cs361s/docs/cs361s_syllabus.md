# UT-Austin CS 361S - Network Security and Privacy

|||
|---|---|
| Instructor: | Seth James Nielson (sethjn@cs.utexas.edu) |
| TA: | Te-Yu Chang (teyu.chang@utexas.edu) |
| Class Times: | Mondays/Wednesdays at 3:30pm |
| Location: | Virtual-Zoom |
| Slack: | fall2021utcs361s.slack.com |
| Professor Office Hours | Immediately after class and by appointment |
| TA Office Hours | 9am-10am Mondays/Tuesdays |

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
of this breadth. In previous semesters, this course had assigned readings
from textbooks. However, the textbooks were terrible.

This semester, you will be assigned a variety of readings from various online
sources. Many will come from Ross Anderson's "Security Engineering" (which is 
excellent!), but the rest will come from many information outlets. This will also
give you ideas for how to research ideas yourself.

*MAJOR DISCLAIMER:* Not all of these readings are great. In fact, many are
perhaps a little bit weak. But instead of making you pay for a textbook with
crappy readings you can get readings of equivalent quality for free.

You will need to search for some readings on your own (e.g., NIST documents, 
RFC, etc.). Here are links to some of the other materials.

1. Ross Anderson, "Security Engineering" **SECOND EDITION**: https://www.cl.cam.ac.uk/~rja14/book.html
2. An Introduction to Computer Networks (ICN): http://intronetworks.cs.luc.edu/current2/html/

### Constructive Concepts

By the end of the course, students are expected to understand the basic concepts
behind constructing a secure network and ensuring privacy. The concepts we will
focus on in class are:

1. What are security properties such as confidentiality, integrity, and authenticity?
1. What are some basic concepts of enforcing security properties such as authentication and authorization?
1. What is the role of cryptography in enforcing security properties?
1. What is the role of secure protocols in enforcing security properties?
1. What is the role of monitoring traffic in enforcing security properties?
1. What are common security techniques in World Wide Web applications?

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
1. What are common problems with World Wide Web security?

# Course Policies

## Subject-to-Change
The instructor sometimes has to make changes to the syllabus. Every possible effort
will be made to protect your grade from these changes.

## Attendance and Preparation
COVID-19 NOTE: Attendance applies as much as possible to virtual
learners. We would like the class to be together (virtually)
during class time. The goal is to ask questions, have discussions,
and learn together.

You must not register for another class whose lecture times 
overlap those of CS 361S, even in part. You must not register 
for a class section whose time overlaps with those of CS 361S, even in part.

Attending lectures and keeping up with the readings is crucial 
for success in CS 361S. You should make every effort to read
the lecture notes and assigned readings before class.

NOTE! It is entirely possible that we will not cover all materials
in a set of lecture notes during the assigned class period. Questions,
discussion, or other influences may prevent us from finishing all
of the content included on the slides. Nevertheless, you are responsible
for all of the material. That is why it is best to read the materials
before class so that the time spent with the professor can be
focused on key ideas, difficult concepts, and so forth.

Please also note that I would like you to participate in class. Every
semester, I only get about 10 percent in-class participation. Please
make an effort to ask questions, to propose discussion topics, or
otherwise engage the professor.

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

## Groups
You will be assigned to a group of four or five students for various purposes
in this course. You will work with your group to discuss readings and to 
debug labs.

## Reading Policy
You are REQUIRED as part of the course to read the materials assigned. To evaluate
your reading, you will virtually meet in a chat-based channel (e.g., slack, text, etc.)
once a week to discuss the reading. The discussion should be no shorter than 20 minutes.
You will send your transcript to the professor and the TA for review. So long as we 
believe, based on the transcript, that you have read the assigned materials, you will
get full credit. There is no partial credit for the readings.

Note, your score is NOT dependent on UNDERSTANDING the material. Your score is dependent on
having read the material and efforts made to understand it. For example, if you read
something that you didn't understand, your score during the discussion might be based
on the insightful questions that you ask your peers or references to other online
sources (even Wikipedia) that you used to try and get a better grasp of the concept.

You need to have your meeting during the following week after the assigned reading.
There are 14 weeks, so there will be 13 group meetings/discussions (we will not 
require you to meet to discuss the last week's readings).

If you struggle to participate in groups like this for any reason (English is your second
language, social anxiety, time pressure, etc.), please contact the professor to work
out a solution.

## Programming Projects
There will be five programming assignments, but one will be done in-class.
So really, it is more like four assignments.

You will need to get a github account and create a private repo
for this course. You need to invite the TA and the professor
to join the repo. You will need to create five top level directories
in your github called "lab1", "lab2", ..., "lab5". Each individual
lab will have instructions on what data needs to be included
in each directory.

Source code for the course will also be made available in
a class github repository. Details will be provided in individual
lab write-ups.

Every student will need to submit their own work and you should
write your own code. You may talk about generic solutions with 
other students and you should definitely feel free to ask questions
on the class Slack.

Under the following very limited conditions, you may show your
code to people within your assigned group.

1. The purpose is for debugging already written code
1. The purpose is NOT for showing the other person what to do or how to do it
1. The other person (or people) looking at your code have also already written code for the equivalent function

In other words, looking at code together should only be done between people
in their assigned groups to help figure out what has gone wrong, not to 
copy another student's work or bypass the steps of figuring out how to get
started.

Obviously, the first lab, which will be done in class, will be a lot
less strict. Please look to each lab write-up for modifications and
details on collaboration.

You SHOULD compare your results with the results of other people in
your assigned group. Especially for the TLS lab, comparing output is
very critical. Labs are pass/fail, so checking that you and your
team are getting the same results are crucial to your grade.

## Exams

There will be two midterm exams. There is no final exam.

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
correct application of these technical concepts to the question. 

Any indication of cheating, such as copying another students
answers, collaborating with another student, communicating with
another human about the test questions, etc. will result in an
automatic 0 on the exam and a full grade deduction (A to B, B+ to C+, etc.).

## Grading

* Labs are strictly Pass/Fail. 12% each (60%)
* Reading discussions (10%)
* Exams. 15% each. (30%)
* 1 Possible extra credit projects.
* Cheating is an automatic fail of the assignment and a full grade deduction.

The reason for pass/fail labs is because many students in the past
have used this as an excuse to not finish the lab. These labs really
don't do much for you unless they are completed.

If a lab is submitted and returned with a 0, you may petition for a
no-penalty resubmission. This will generally be allowed where there is a clear
indication that you submitted something that should have reasonably worked,
but failed because of something unexpected or unclear in the lab requirements.
Please note, YOU WILL NOT BE ALLOWED TO RESUBMIT IF YOU DID NOT
COMPARE YOUR RESULTS WITH A TEAMMATE BEFORE SUBMISSION. You must include
your comparison data as part of your petition for a regrade. 

Labs are marked down 10 percent per day late.

Grading scale is standard:

* 93 -100 - A
* 90 - 93 - A-
* 87 - 90 - B+
* 84 - 87 - B
* 80 - 83 - B-
* 77 - 80 - C+
* 73 - 77 - C
* 70 - 73 - C-
* 67 - 70 - D+
* 63 - 67 - D
* 60 - 63 - D-
* Less than 60 - E

One A+ may be issued to the top student if her or his grade is
above 100 percent and not tied with any other students.

# Calendar

||||
|---|---|---|
| Date | Lecture | Assignments |
| 1/20 |  Introduction to Network Security | Assigned: reading 1 |
| 1/25 |  Networking Background (Protocols) | Assigned: reading 2 |
| | | Due: reading 1 |
 | 1/27 |  Networking Background (Architecture) | Assigned: reading 3 |
| | | Due: reading 2 |
 | 2/1 |  Classic Network Security Problems | Due: reading 3 |
| | | Due week 1 discussion (reading 1) |
| 2/3 |  In class Networking/Wireshark Exercises | Assigned: lab 1, reading 4 |
| 2/8 |  Security Objectives and Ross Anderson's "Security Policies" | Assigned: reading 5 |
| | | Due: reading 4 |
| | | Due: week 2 discussion (reading 2 and 3) |
 | 2/10 |  Authentication | Assigned: reading 6 |
| | | Due: reading 5, lab 1 |
| 2/15 | Ice-pocalypse 2021 |
| 2/17 | Ice-pocalypse 2021 |
| 2/22 | Ice-pocalypse 2021 | 
 | 2/24 |  Authorization and Access Controls | Assigned: reading 7, lab 2 |
| | | Due: reading 6 |
| | | Due: week 3 discussion (reading 4 and 5) | 
 | 3/1 |  Intro to Crypto | Assigned: reading 8 |
| | | Due: reading 7 |
| | | Due: week 4 discussion (reading 6) |
 | 3/3 |  Symmetric Crypto | Assigned: reading 9 |
| | | Due: reading 8 |
 | 3/8 |  Asymmetric Crypto | Assigned: reading 10 |
| | | Due: reading 9 |
| | | Due: week 5 discussion (reading 7 and 8) |
 | 3/10 |  TLS and Kerberos, PKI | Assigned: reading 11, reading 12 |
| | | Due: reading 10, lab 2 |
| 3/22 |  Malware - Viruses, Trojans, Ransomware | Assigned: reading 13, lab 3 |
| | | Due: reading 11, 12 |
 | 3/24 |  Malware Detection Challenges | Assigned: reading 14 |
| | | Due: reading 13 |
 | 3/29 |  Host Security and Vulnerabilities | Assigned: reading 15 |
| | | Due: reading 14 |
 | 3/31 |  Why Vulnerabilities are Hard | Assigned: lab 4 |
| | | Due: reading 15, lab 3 |
 | 4/5 |  Perimeter Security Technologies | Assigned: reading 17 |
| 4/7 |  Perimeter Security Architectures | Assigned: reading 18 |
| | | Due: reading 17 |
 | 4/12 |  HTTP and the World Wide Web | Assigned: reading 19 |
| | | Due: reading 18 |
 | 4/14 |  Web Threats and Defenses I | Assigned: reading 20 |
| | | Due: reading 19, lab 4 |
 | 4/19 |  Web Threats and Defenses II | Assigned: reading 21, lab 5 |
| | | Due: reading 20 |
 | 4/21 |  Overlay Network Threats - Email, Social Media | Assigned: reading 22 |
| | | Due: reading 21 |
 | 4/26 |  Advanced Topics - Zero Trust | Assigned: reading 23 |
| | | Due: reading 22 |
 | 4/28 |  Advanced Topics - Blockchain/Consensus | Due: reading 23 |
| 5/3 |  EXAM REVIEW | Due: lab 5 |
| 5/5 |  MIDTERM EXAM 2 |  |

# Readings
* reading 1 -  ICN 1.1-1.5, 1.8-1.15, 9.1-9.7, 11.1-11.3, 16.1, 17.1-17.4, 17.7
* reading 2 -  ICN 10, 15, https://cyber.harvard.edu/digitaldemocracy/internetarchitecture.html, https://students.mimuw.edu.pl/~zbyszek/sieci/CCNA4%20Sample.pdf
* reading 3 -  Ross Anderson 21.1-21.2
* reading 4 -  Ross Anderson 1, NIST 800-12 section 2
* reading 5 -  http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.26.153&rep=rep1&type=pdf Sections 1-2, https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=8784263, Skim Ross Anderson 15.3-15.8, read 15.9
* reading 6 -  http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.26.153&rep=rep1&type=pdf Section 3, Ross Anderson 8
* reading 7 -  Ross Anderson 5.1-5.2
* reading 8 -  Ross Anderson 5.3-5.3.3, 5.4.2, 5.5
* reading 9 -  Ross Anderson  5.3.4-5.3.5, 5.7
* reading 10 -  TLS 1.2 RFC 5246, Kerberos v5 RFC 1510, see also wikipedia's entry on Kerberos
* reading 11 -  https://buildmedia.readthedocs.org/media/pdf/pki-tutorial/latest/pki-tutorial.pdf
* reading 12 -  https://www.mcafee.com/enterprise/en-us/assets/white-papers/wp-understanding-ransomware-strategies-defeat.pdf, https://www.virusbulletin.com/uploads/pdf/magazine/1991/199111.pdf
* reading 13 -  https://www.cs.virginia.edu/~evans/pubs/virus.pdf
* reading 14 -  https://www.cs.utexas.edu/~shmat/courses/cs380s_fall09/cowan.pdf, https://inst.eecs.berkeley.edu/~cs161/fa08/papers/stack_smashing.pdf
* reading 15 -  http://www.dullien.net/thomas/weird-machines-exploitability.pdf
* reading 16 -  https://students.mimuw.edu.pl/~zbyszek/sieci/CCNA4%20Sample.pdf, NIST 800-41r1
* reading 17 -  https://www.giac.org/paper/gppa/548/deploying-honeypots-security-architecture-fictitious-company/105318
* reading 18 -  https://www.inspirisys.com/HTTP_Protocol_as_covered_in_RFCs-An_Overview.pdf, https://www.giac.org/paper/gsec/226/cookie-crumbs-introduction-cookies/100727, https://www.cs.princeton.edu/courses/archive/spr17/cos598D/NarrowWaist10.pdf
* reading 19 -  https://owasp.org/www-project-top-ten/ and immediate subpages for the top 10, https://www.youtube.com/watch?v=9kaihe5m3Lk and the example embedded
* reading 20 -  https://owasp.org/www-chapter-london/assets/slides/OWASPLondon20171130_Cookie_Security_Myths_Misconceptions_David_Johansson.pdf, https://www.usenix.org/system/files/conference/usenixsecurity15/sec15-paper-zheng.pdf
* reading 21 -  http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.59.9431&rep=rep1&type=pdf, https://www.sans.org/reading-room/whitepapers/email/spam-anti-spam-1776
* reading 22 -  https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/44860.pdf
* reading 23 -  https://www.scs.stanford.edu/17au-cs244b/labs/projects/porat_pratap_shah_adkar.pdf

# Labs
* lab 1 -  In class lab work
* lab 2 -  Authentication/Authorization lab
* lab 3 -  TLS 1.2 Server and Interceptor
* lab 4 -  ROP lab
* lab 5 -  Capture the Flag Exercises