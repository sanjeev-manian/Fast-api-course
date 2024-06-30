# print("hello world!")
# cost = 10
# print(cost)
# print(10 + 10 * 10)
# username = "sanjeev"
# password = "kumar"
# print(username, password)
# print(f"hi {username}")
# days = int(input("Enter your first name : "))
# print(round(days / 3, 2))
# my_list = {80, 60, 70, 10, 60}
# my_tuple = (80, 60, 70, 10, 60)
# print(my_tuple[2])
# my_list.append("kumar")
# my_list.append(45)
# my_list.pop(0)
# my_list.remove(60)
# my_list.add(89)
# my_list.update(
#     [
#         90,
#     ]
# )
# for x in my_list:
#     print(x)
# if 2 == 1:
#     print("sanjeev")
# elif not (3 == 3 and 5 < 3):
#     print("M<")
# else:
#     print("Kumar")
# print("hello")
# i = 0
# while i < 5:
#     i += 1
# else:
#     print(i)
# my_vehicle = {"model": "Ford", "make": "Explorer", "year": 2018, "mileage": 40000}
# for i, j in my_vehicle.items():
#     print(f"{i}: {j}")


def my_function(name: str, password: str) -> bool:
    """Check whether the name password matches.

    Args:
        name (str): name of the user
        password (str): password of user

    Returns:
        bool: returns if matches
    """
    print(name, password)
    return True


def data_of_user(name: str, password: str, age: int) -> dict:
    """Check whether the name password matches.

    Args:
        name (str): name of the user
        password (str): password of user

    Returns:
        bool: returns if matches
    """
    bio_data = {"name": name, "password": password, "age": age}
    return bio_data


# print(data_of_user(password="sanjeev", name="kumar", age=44))
