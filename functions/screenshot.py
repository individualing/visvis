
import visvis as vv
import numpy as np


def getCardinalSplineCoefs(t, tension=0.0):
    
    # Init
    t = float(t)
    c = [0 for i in range(4)]
    tau  = 0.5*(1-tension)
    
    # Calc coefs
    c[0] = - tau * (   t**3 - 2*t**2 + t )
    c[3] =   tau * (   t**3 -   t**2     )
    c[1] =           2*t**3 - 3*t**2 + 1  - c[3]
    c[2] = -         2*t**3 + 3*t**2      - c[0]
    
    # Done
    return c


def screenshot(filename, ob, scaleFactor=3, tension=-0.25):
    """ screenshot(ob, filename, scaleFactor=3, tension=-0.25)
    Uses vv.getframe(ob) to obtain the image in the figure or axes.
    Then uses vv.imwrite(filename, ..) to store the resulting image.
    
    In between the image is interpolated using the given scale factor
    using high quality bicubic interpolation. The tension controls the
    responsivenes of the filter. The more negative, the more overshoot,
    but the more it is capable to make for example font glyphs smooth.
    If tension is 0, the interpolator is a Catmull-Rom spline.
    
    I filename is None, the interpolated image is returned as a numpy
    array.
    """
    
    # Scale must be integer, calc amount of pixels in between 
    s = int(scaleFactor)
    inBetween = s-1
    
    # Obtain image
    im1 = vv.getframe(ob)
    shape1 = im1.shape
    
    # Pad original image, so we have no trouble at the edges
    shape2 = shape1[0]+2, shape1[1]+2, 3
    im2 = np.zeros(shape2, dtype=np.float32) # Also make float
    im2[1:-1,1:-1,:] = im1
    im2[0,:,:] = im2[1,:,:]
    im2[-1,:,:] = im2[-2,:,:]
    im2[:,0,:] = im2[:,1,:]
    im2[:,-1,:] = im2[:,-2,:]
    
    # Create empty new image. It is sized by the scaleFactor, 
    # but the last row is not. 
    shape3 = (shape1[0]-1)*s+1, (shape1[1]-1)*s+1, 3    
    im3 = np.zeros(shape3, dtype=np.float32)
    
    # Fill in values!
    for dy in range(s+1):
        for dx in range(s+1):
            
            # Get interpolation fraction and coefs
            ty = float(dy)/s
            tx = float(dx)/s
            cy = getCardinalSplineCoefs(ty, tension)
            cx = getCardinalSplineCoefs(tx, tension)
            
            # Create tmp image to which we add the contributions
            # Note that this image is 1 pixel smaller in each dimension.
            # The last pixel is filled because dy and dx iterate INCLUDING s.
            shapeTmp = shape1[0]-1, shape1[1]-1, 3
            imTmp = np.zeros(shapeTmp, dtype=np.float32)
            
            # Collect all 16 neighbours and weight them apropriately
            for iy in range(4):
                for ix in range(4):
                    
                    # Get weight
                    w = cy[iy]*cx[ix]
                    if w==0:
                        continue
                    
                    # Get slice. Note that we start at 0,1,2,3 rather than
                    # -1,0,1,2, because we padded the image.
                    D = {0:-3,1:-2,2:-1,3:None}
                    slicey = slice(iy, D[iy])
                    slicex = slice(ix, D[ix])
                    
                    # Get contribution and add to temp image
                    imTmp += w * im2[slicey, slicex, :]
            
            # Store contributions            
            D = [-1 for tmp in range(s)]; D.append(None)
            slicey = slice(dy,D[dy],s)
            slicex = slice(dx,D[dx],s)
            im3[slicey, slicex, :] = imTmp
    
    
    # Correct for overshoot
    im3[im3>1]=1
    im3[im3<0]=0
    
    # Store image to file
    if filename is not None:
        vv.imwrite(filename, im3)
    else:
        return im3
        
    #vv.screenshot('d:/almar/projects/ims/test0.png', vv.gcf())
    