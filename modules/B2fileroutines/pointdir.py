"""
Boundaries of EISCAT scan azimuth/elevation
calculated as convex hull of point directions projected on complex plane,
and returned in az/el coordinates

NB: Rounding all values to 1 or 2 decimals
"""

class AzEl:
    
    def __init__(self,az,el):

        self.az=az
        self.el=el
        
    def boundary(self):
    
        import numpy as np
        import scipy.spatial as sp
        import cmath

        npoints=len(self.az)
        assert npoints==len(self.el)

        ## project to polar points (azimuth angle [rad], zenith angle [degrees]) in cartesian system
        grid=np.zeros((len(self.az),2))    

        for k in range(npoints):
    
            # Azimuth
            phi=round(900.0-10.0*self.az[k])/10.0
            if phi<0:
                phi=phi+360.0
            phi=phi*np.pi/180.0
        
            #Zenith angle degrees
            r=round(900.0-10.0*self.el[k])/10.0
            
            # projection to plane
            z=cmath.rect(r,phi)
            grid[k,0]=z.real
            grid[k,1]=z.imag

        ## ensure grid of unique directions
        uniq_grid=[]
            
        for p in grid:
            #comparison works between lists of lists, not numpy arrays
            #so convert
            d=[round(10.0*val)/10.0 for val in p] 
            if d not in uniq_grid:
                uniq_grid.append(d)
                    
        #back to array
        uniq_grid=np.array(uniq_grid)
    
        ## Boundary of direction points
        if len(uniq_grid) <= 3:
            # grid of <=3 points can be returned as is
            dirs=[cmath.polar(point) for point in (uniq_grid[:,0]+1.0j*uniq_grid[:,1])]
        else:
            # return boundary: convex hull of projected direction
            hull=sp.ConvexHull(uniq_grid)
            dirs=[cmath.polar(point) for point in (uniq_grid[hull.vertices,0]+1.0j*grid[hull.vertices,1])]

        ## Return pointing directions in EISCAT [azimuth,elevation] coordinates
        points=[[round(900.0-10.0*dir[1]*180.0/np.pi)/10.0 if dir[1]*180.0/np.pi<=90.0 else round(4500.0-10.0*dir[1]*180.0/np.pi)/10.0, round(900.0-10.0*dir[0])/10.0] for dir in dirs]
        return points
