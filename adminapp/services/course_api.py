import requests


def get_courses_from_api():

    url = "https://dummyjson.com/products"

    response = requests.get(url)

    if response.status_code == 200:

        data = response.json()

        courses = []

        course_names = [
            "Python Programming",
            "Web Development",
            "Database Management System",
            "Data Structures",
            "Java Programming",
            "Computer Networks",
            "Software Engineering",
            "Artificial Intelligence",
            "Machine Learning",
            "Cloud Computing"
        ]

        descriptions = [
            "Learn Python programming from basics to advanced concepts.",
            "Learn HTML, CSS, JavaScript and modern web development.",
            "Learn database concepts, SQL, normalization and transactions.",
            "Learn arrays, linked lists, stacks, queues, trees and graphs.",
            "Learn Java programming, OOP concepts and application development.",
            "Learn computer networking, TCP/IP, routing and network protocols.",
            "Learn software development life cycle, testing and software design.",
            "Learn artificial intelligence concepts, search algorithms and knowledge representation.",
            "Learn machine learning concepts, algorithms and model development.",
            "Learn cloud computing concepts, services, virtualization and deployment."
        ]

        for i in range(10):

            course = {
                "title": course_names[i],
                "description": descriptions[i],
                "course_code": f"LMS-{i + 1:03d}"
            }

            courses.append(course)

        return courses

    return []