# UT-Austin CS 361S - Network Security and Privacy

|||
|---|---|
| Instructor: | Seth James Nielson (sethjn@cs.utexas.edu) |
| TA: | Syamantak Kumar (syamantak@utexas.edu) |
| Class Times: | Mondays/Wednesdays at 2:00pm |
| Location: | Virtual-Zoom |
| Slack: | fall2021utcs361s.slack.com |
| Professor Office Hours | By appointment |
| TA Office Hours | Thursday 3-4 PM (Desk 1) |

# Virtual Instruction

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

# University Suggested or Required Disclosures

## Covid, Vaccinations, Masks, and other Public Safety Issues
As this class meets virtually, most of these issues are irrelevant
for our purposes. However, there will most likely be some in-person
contact with the professor, the TA, and/or other classmates. For
these situations in particular, please consider the following
recommendations from the Unviersity:

* Adhere to university [mask guidance](https://utexas.box.com/s/ymob0b4vimv4j9gnhskpsqywwadk3f10).
* [Vaccinations are widely available](https://uthealthaustin.org/patient-resources/covid-19-updates/covid-19-vaccination), free and not billed to health insurance. The vaccine will help protect against the transmission of the virus to others and reduce serious symptoms in those who are vaccinated.
* [Proactive Community Testing](https://healthyhorns.utexas.edu/coronavirus_proactive_testing.html) remains an important part of the university’s efforts to protect our community. Tests are fast and free.
* Visit [protect.utexas.edu](protect.utexas.edu) for more information.


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

# Additional Information about Covid Vaccinations, Testing, Etc
At the time of this writing, masking is optional. When meeting in person,
you _may_ wear masks but are not required to do so. Please pay attention
to university announcements in case this changes.

I cannot stress enough how valuable vaccination is. However, not only
am I prohibited from asking about your vaccination status, I wouldn't 
inquire in any event. You will not be pressured in any way to disclose
this information from the professor or the TA.

Where things can be difficult is when students have to work together
in person. If you, personally, only wish to meet with masked and/or
vaccinated students, I am not sure how to handle your request. Please
talk to me and I will see how to proceed.

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
Attendance applies as much as possible to virtual
learners. We would like the class to be together (virtually)
during class time. The goal is to ask questions, have discussions,
and learn together. We will also do practical mini-labs
in class that will count toward your final grade.

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
Your instructor is an adjunct faculty; that means I am not on campus
regularly and do not have an office. However, I make an effort to be
available throughout the week. Please schedule a time to meet with me
or ask me questions on slack.

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
You will send your transcript to the TA for review. So long as we 
believe, based on the transcript, that you have read the assigned materials, you will
get full credit. There is no partial credit for the readings.

Note, your score is NOT dependent on UNDERSTANDING the material. Your score is dependent on
having read the material and efforts made to understand it. For example, if you read
something that you didn't understand, your score during the discussion might be based
on the insightful questions that you ask your peers or references to other online
sources (even Wikipedia) that you used to try and get a better grasp of the concept.

Each group discussion transcript is due to the TA the first class period in the week following
the discussion. That means there is a three week operating period for eaching reacing:

* Week 1: Read assignments
* Week 2: Discuss assignments
* Week 3: Turn in discussion transcript

The weeks are calendar weeks. That means that sometimes there will be one reading assignment
in the week (because there is only one class day) and other times there will be two. Sometimes
you will have a full week of class days to do the discussion and sometimes your discussion week
will be truncated. Sometimes the transcript will be due on a Monday and sometimes on a Wednesday.
But the schedule is very simple. What you read one week you discuss the next. What you discuss one
week you turn in the next. If a full week of school is missing (e.g., spring break), discussions
(and therefore submissions) are delayed a week.

*THERE WILL BE NO DISCUSSIONS ASSIGNED FOR THE LAST WEEK's READINGS.* For the second to last week
of readings, which would technically not be due until after class ends, you may submit by the
assigned date of the class's final exam.

If you struggle to participate in groups like this for any reason (English is your second
language, social anxiety, time pressure, etc.), please contact the professor to work
out a solution.

## Programming Projects
There will be six programming assignments as well as mini-labs that will be
done in class.

You will need to get a github account and create a private repo
for this course. You need to invite the TA and the professor
to join the repo. You will need to create six top level directories
in your github called "lab1", "lab2", ..., "lab6". Each individual
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
very critical. Labs have required elements that, if missing, result
in an automatic fail, so checking that you and your
team are getting the same results are crucial to your grade.

## Exams

There are no exams in this class

## Grading

* Labs. 10% each (60%)
* In-class mini-labs (30%)
* Reading discussions (10%)
* 1 Possible extra credit projects.
* Cheating is an automatic fail of the assignment and a full grade deduction.

Labs have a minimum set of requirements to get 80 percent. If these
requirements are not met, the lab is graded as a 0. The reason for
this policy is because many students in the past
have used partial credit as a way to pass the class without learning
the material. 

If a lab is submitted and returned with a 0, you may petition for a
no-penalty resubmission. This will generally be allowed where there is a clear
indication that you submitted something that should have reasonably worked,
but failed because of something unexpected or unclear in the lab requirements.
Please note, YOU WILL NOT BE ALLOWED TO RESUBMIT IF YOU DID NOT
COMPARE YOUR RESULTS WITH A TEAMMATE BEFORE SUBMISSION. You must include
your comparison data as part of your petition for a regrade. 

This class does not have a final exam. However, you may resubmit any one lab
for a full credit re-grade by the date scheduled for the final (exact date TBD).

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
| Date | Lecture                               | Assignments |
| 8/25 | Security Objectives and Policies      | Assigned: reading 1 |
| 8/30 | Mini-lab 1: Buffer overflow and GDB   | Assigned: reading 2 |
| 9/1  | Overview of Lab 1                     | Assigned: lab 1 |
| 9/8  | Buffer overflow and ROP               | Assigned: reading 3 |
|      |                                       | Due: Discussion |
| 9/13 | Mini-lab 2: Hub and Spoke, Wireshark  | Assigned: reading 4 |
| 9/15 | Overview of Lab 2                     | Assigned: lab 2 |
|      |                                       | Assigned: reading 5 |
|      |                                       | Due: Lab 2 |
| 9/20 | Networking Background                 | Assigned: reading 6 |
| 9/22 | Access Controls                       | Assigned: reading 7 |
| 9/27 | Authenticaiton and Authorization      | Assigned: reading 8 |
| 9/29 | Overview of Lab 3                     | Assigned: reading 9 |
|      |                                       | Assigned: lab 3 |
|      |                                       | Due: Lab 2 |
| 10/4 | Mini-lab 3: Symmetric Cryptography    | Assigned: reading 10 |
| 10/6 | Symmetric Cryptography                | Assigned: reading 11 |
| 10/11| Mini-lab 4: Asymmetric Cryptography   | Assigned: reading 12 |
| 10/13| Overview of Lab 4                     | Assigned: reading 13 |
|      |                                       | Assigned: Lab 4 |
|      |                                       | Due: ~~Lab 3~~ |
| 10/18| Asymmetric Crypto                     | Assigned: reading 14 |
| 10/20| TLS and Kerberos, PKI                 | Assigned: reading 15 |
| 10/25| Help Section                          | Assigned: reading 16 |
|      | ~~Mini-lab 5: HTTP and Web~~          | |
| 10/27| Mini-lab 5: HTTP and Web              | Assigned: reading 17 |
|      | ~~Overview of Lab 5~~                 | Assigned: ~~Lab 5~~ |
|      |                                       | Due: ~~Lab 4~~ |
| 11/1 | HTTP and Web                          | Assigned: reading 18 |
|      |                                       | Due: Lab 3 and Lab 4 |
| 11/3 | OAuth protocol                        |  |
| 11/8 | Mini-lab 6: Cookies                   | Assigned: reading 19 |
| 11/10| Overview of Lab 6                     | Assigned: reading 20 |
|      |                                       | Due: Lab 5 |
| 11/15| Web Privacy                           | Assigned: reading 21 |
| 11/17| XSS and Web Threats                   | Assigned: reading 22 |
| 11/22| Malware and Detection                 | Assigned: reading 23 |
| 11/30| Perimeter Security                    | Assigned: reading 24 |
|      |                                       | Due: Lab 6 |
| 12/1 | Email Security                        | Assigned: reading 25 |
| 12/6 | APT & Zero Trust                      |  |
|      |                                       | Due: Makeup/Xtra Labs |


# Readings
* reading 1 -  Ross Anderson 1, NIST 800-12 section 2
* reading 2 -  https://www.cs.utexas.edu/~shmat/courses/cs380s_fall09/cowan.pdf, https://inst.eecs.berkeley.edu/~cs161/fa08/papers/stack_smashing.pdf
* reading 3 -  https://hovav.net/ucsd/dist/rop.pdf
* reading 4 -  ICN 1.1-1.5, 1.8-1.15, 9.1-9.7, 11.1-11.3, 16.1, 17.1-17.4, 17.7
* reading 5 -  ICN 10, 15, https://cyber.harvard.edu/digitaldemocracy/internetarchitecture.html, https://students.mimuw.edu.pl/~zbyszek/sieci/CCNA4%20Sample.pdf
* reading 6 -  http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.26.153&rep=rep1&type=pdf Section 3, Ross Anderson 8
* reading 7 -  http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.26.153&rep=rep1&type=pdf Sections 1-2, https://ieeexplore.ieee.org/stamp/stamp.jsp?arnumber=8784263, Skim Ross Anderson 15.3-15.8, read 15.9
* reading 8 -  TLS 1.2 RFC 5246
* reading 9 -  Ross Anderson 5.2, https://cryptography.io/en/latest/hazmat/primitives/symmetric-encryption/
* reading 10 - Ross Anderson 5.3.1-5.3.3, 5.5, https://cryptography.io/en/latest/hazmat/primitives/mac/, https://cryptography.io/en/latest/hazmat/primitives/aead/
* reading 11 - Ross Anderson 5.3.4-5.3.5, https://cryptography.io/en/latest/hazmat/primitives/asymmetric/
* reading 12 - Ross Anderson 5.7
* reading 13 - TLS 1.2 RFC 5246, , Kerberos v5 RFC 1510, see also wikipedia's entry on Kerberos 
* reading 14 - https://buildmedia.readthedocs.org/media/pdf/pki-tutorial/latest/pki-tutorial.pdf
* reading 15 - https://www.inspirisys.com/HTTP_Protocol_as_covered_in_RFCs-An_Overview.pdf, RFC 2616
* reading 16 - https://www.giac.org/paper/gsec/226/cookie-crumbs-introduction-cookies/100727
* reading 17 - https://developer.okta.com/blog/2019/10/21/illustrated-guide-to-oauth-and-oidc
* reading 18 - RFC 6749, https://openid.net/specs/openid-connect-basic-1_0.html
* reading 19 - https://owasp.org/www-project-top-ten/ and immediate subpages for the top 10
* reading 20 -  https://owasp.org/www-chapter-london/assets/slides/OWASPLondon20171130_Cookie_Security_Myths_Misconceptions_David_Johansson.pdf, https://www.usenix.org/system/files/conference/usenixsecurity15/sec15-paper-zheng.pdf
* reading 21 - https://www.youtube.com/watch?v=9kaihe5m3Lk and the example embedded, https://www.cs.princeton.edu/courses/archive/spr17/cos598D/NarrowWaist10.pdf
* reading 22 - https://www.cs.virginia.edu/~evans/pubs/virus.pdf, http://www.dullien.net/thomas/weird-machines-exploitability.pdf
* reading 23 - https://students.mimuw.edu.pl/~zbyszek/sieci/CCNA4%20Sample.pdf, NIST 800-41r1, Ross Anderson 21.1-21.2
* reading 24 - https://www.sans.org/reading-room/whitepapers/email/spam-anti-spam-1776, http://citeseerx.ist.psu.edu/viewdoc/download?doi=10.1.1.59.9431&rep=rep1&type=pdf, https://www.theengineroom.org/wp-content/uploads/2020/08/OrgSec-Case-study-Spearphishing-attacks-June-2020.pdf,
https://www.mcafee.com/enterprise/en-us/assets/white-papers/wp-understanding-ransomware-strategies-defeat.pdf
* reading 25 - https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/44860.pdf,
https://www.lockheedmartin.com/content/dam/lockheed-martin/rms/documents/cyber/Gaining_the_Advantage_Cyber_Kill_Chain.pdf,
https://roselabs.nl/files/audit_reports/Fox-IT_-_DigiNotar.pdf



# Labs
* Mini-Lab - Buffer Overflow and GDB
* Mini-Lab - Class Hub and Spoke, Wireshark
* Mini-Lab - Cryptography 1
* Mini-Lab - Cryptography 2
* Mini-Lab - HTTP and Web
* Mini-Lab - Cookies

* lab 1 -  ROP lab
* lab 2 -  Authentication/Authorization
* lab 3 -  TLS 1.2 Server
* lab 4 -  TLS Interceptor/Visibility
* lab 5 -  OAuth SSO
* lab 6 -  Capture the Flag Exercises