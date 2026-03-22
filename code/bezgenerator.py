import random
import math
import numpy as np

def generate_bez(screen_width,num_small_curves):

    control_points = []
    main_points = []
    curves = []

    '''
    here I am generating the coordinates for all the control points for each small curve
    then i am generating the coordinates for the main points between each control point
    and finally calling the generate_bez function to generate all the points that will lie on the track
    '''

    # evenly spaced out position for control points,
    # it goes to 100000 because the player will never go that far
    pos = np.linspace(1000, 100000, num_small_curves)

    control_points.append((screen_width/2, 980))
    control_points.append((screen_width/2, 0))
    # I am putting 2 points on the track that will definitely be there for all games
    # this way the start of the track will always be straight

    for i in range(num_small_curves):
        # x-coordinate of control point is
        # random within the dimensions of the screen
        x = random.randint(0,screen_width)
        y = -pos[i]
        control_points.append((x, y))

    for j in range(num_small_curves):
        # the main point coordinates are half way
        # along the lines connecting consecutive control points
        if j<(num_small_curves-1):
            x =  (control_points[j][0]+control_points[j+1][0])//2
            y = (control_points[j][1]+control_points[j+1][1])//2

        # this is at the end of the track,
        # the main points wont move so the track ends
        else:
            x = (control_points[j][0] + control_points[j][0]) // 2
            y = (control_points[j][1] + control_points[j][1]) // 2
        main_points.append((x,y))

    for k in range(num_small_curves):

        if k<(num_small_curves-1):
            current = [main_points[k],control_points[k+1],main_points[k+1]]
            # current holds all the information needed
            # for each individual small curve to then use generate_bez

        else:
            current = [main_points[k], control_points[0], main_points[0]]
        curve = bezier_curve(np.array(current),int(9000/num_small_curves))
        # (9000/num_small_curves) so that the number of points on each small curve
        # is inversely proportional to number of small curves
        curves.append(curve)

    # I could only return 'curves' but control
    # and main points were helpful for debugging
    return curves,control_points,main_points

def bezier_curve(control_points, num_points):

    '''This function takes control points and the number of points you want on each
    small curve, and outputs the coordinates of all the points that will lie on the curve.
    While I am only taking 3 control points as every time, I am using the general formula for the bezier curve
    rather than the quadratic so that i have more flexibility in case i decided to change the number of control points
    '''

    n = len(control_points) - 1

    t = np.linspace(0, 1, num_points)
    curve = np.zeros((num_points, 2))

    for i in range(num_points):
        for j in range(n + 1):

            #this is the formula mentioned in the document
            curve[i] += (control_points[j]
                * (
                    math.factorial(n)/ (math.factorial(j) * math.factorial(n - j))
                )
                * t[i] ** j
                * (1 - t[i]) ** (n - j)
            )
    return curve # curve is a list of tuples, each tuple is a point that lies on the curve