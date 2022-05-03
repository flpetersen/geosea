#Define parameters

import numpy as np
from numpy.linalg import inv
    
def nadjust2D(m = None,xinp = None,std_M = None,num_transp = None,num_baselines = None,id = None,bsl_reference = None): 
    
    bx = sym('x',np.array([1,num_transp]))
    by = sym('y',np.array([1,num_transp]))
    ## Set Parameters
    pp = 0
    n = 0
    g = 0


    C_weight, j_inp, xy, G, L = list()

    for i in np.arange(1,num_transp+1).reshape(-1):
        G = np.array([[G],[1,0],[0,1]])
        j_inp = np.array([j_inp,bx(i),by(i)])
        for j in np.arange(1,num_transp+1).reshape(-1):
            if j != i:
                pp = (np.array([pp,i]))
                if ismember(j,pp):
                    continue
                else:
                    g = g + 1
                    if bsl_reference(g) == 1:
                        n = n + 1
                        L = np.array([[L],[m(n)]])
                        d[n] = np.sqrt((bx(i) - bx(j)) ** 2 + (by(i) - by(j)) ** 2)
                        C_weight = np.array([C_weight,0.05 ** 2])
    
    ## Jacobi matrix
    
    J = jacobian(d,j_inp)
    ## Distance functions
    
    k = 1
    h = 1
    for i in np.arange(1,num_transp+1).reshape(-1):
        for j in np.arange(1,num_transp+1).reshape(-1):
            if j != i:
                pp = (np.array([pp,i]))
                if j in pp:
                    continue
                else:
                    g = g + 1
                    if bsl_reference(g) == 1:
                        n = n + 1
                        d[n] = np.sqrt((xinp(k) - xinp(h)) ** 2 + (xinp(k + 1) - xinp(h + 1)) ** 2)
            h = h + 2
        k = k + 2
    
    d = np.transpose(d)
    C = np.diag(np.array([C_weight]))
    ## Input Coordinates
    
    if num_transp >= 5:
        x1 = xinp(1)
        y1 = xinp(2)
        x2 = xinp(3)
        y2 = xinp(4)
        x3 = xinp(5)
        y3 = xinp(6)
        x4 = xinp(7)
        y4 = xinp(8)
        x5 = xinp(9)
        y5 = xinp(10)
    
    if num_transp >= 6:
        x6 = xinp(11)
        y6 = xinp(12)
    
    if num_transp >= 7:
        x7 = xinp(13)
        y7 = xinp(14)
    
    if num_transp >= 8:
        x8 = xinp(15)
        y8 = xinp(16)
    
    if num_transp >= 9:
        x9 = xinp(17)
        y9 = xinp(18)
    
    if num_transp >= 10:
        x10 = xinp(19)
        y10 = xinp(20)
    
    if num_transp >= 11:
        x11 = xinp(21)
        y11 = xinp(22)
    
    if num_transp >= 12:
        x12 = xinp(23)
        y12 = xinp(24)
    
    if num_transp >= 13:
        x13 = xinp(25)
        y13 = xinp(26)
    
    if num_transp >= 14:
        x14 = xinp(27)
        y14 = xinp(28)
    
    ##
    L0 = eval(d)
    ## Inversion of covariance matrix tp wheight matrix
    
    ## Array of Baselines
    
    ## Adjustment
    
    x0 = np.transpose(xinp)
    A = eval(J)
    
    #C=diag([((th1/1000)*0.0028)^2 ((th2/1000)*0.0028)^2 ((th3/1000)*0.0028)^2 ((th4/1000)*0.0028)^2 ((th5/1000)*0.0028)^2 ((th6/1000)*0.0028)^2 ((th7/1000)*0.0028)^2 ((th8/1000)*0.0028)^2 ((th9/1000)*0.0028)^2 ((th10/1000)*0.0028)^2 ]);
    
    #C=diag(std_M);
    
    P = inv(C)
    w = L0 - L
    u = np.transpose(A) * P * w
    N1 = np.transpose(A) * P * A + G * np.transpose(G)
    ## x-y Translation
    d = - inv(N1) * np.transpose(A) * P * A * inv(N1) * u

    ## New Coordinates
    xa = x0 + d

    ## Cofactor Matrix of adjused coordinates

    #determine cofactor matrix Qx of adjusted parameters, residuals and aposteriori variance s02
    
    Qx = inv(N1) * np.transpose(A) * P * A * inv(N1)
    ## residuals
    v = A * d + w
    ## aposteriori variance S02
    s02 = np.transpose(v) * P * v / (2)

    return (xa,v,s02,d,P,C)
    
