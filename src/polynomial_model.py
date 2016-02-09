import random
import math
import json

def binomial(n,p):
    return math.factorial(n)/(math.factorial(p)*math.factorial(n-p))

def add_vectors(a, b):
    res = ()
    for i in range(len(a)):
        res+=(a[i]+b[i],)
    return res

class PolynomialModel():


    def __init__(self, in_dim, out_dim, max_poly_deg, q_home):
        """Generate all the necessary component of the model, including the
        polynomial corresponding to the given dimensions and degree, and the
        adjustable parameters matrix.

        Notes :
            * q_home is specific for this model (we need all the initial
            results to be around q_home)
            * params is a matrix of size (out_dim, nb_term)
        """
        self.in_dim = in_dim
        self.out_dim = out_dim
        self.max_poly_deg = max_poly_deg
        self.q_home = q_home

        self.alpha = 0.2 # gradient step
        self.in_magnitude = 0.2 # the range in which input terms are
        self.out_magnitude = math.pi # the range inwhich output terms are
        self.random_spread = 0.01 # how much around q_home are the initial params
        self.generate_polynomial()
        self.generate_params()

    def set_alpha(self, alpha):
        self.alpha = alpha

    #def dataset_preprocess(self, dataset):
        # we can dramatically improve the function performance :
        # when compute is called by the trainer function we recalculate
        # the polynomial transformation of the point (order P).
        # BUT the dataset doesn't change over the training, so we can calculate
        # it only at the initialization
        # but how to implement it ?

    def generate_polynomial(self):
        """Generate the polynomial.

        The polynomial used in this model have multiple indeterminates (one
        indeterminate per input dimension).
        We can see each term of this polynomial as a vector of in_dim dimension
        where each component is an int coding for the indeterminate degree in
        the term.
        The polynomial is eventually a set of terms

        For example :
            * We have an input dimension of three : (x,y,z)
            * The second degree polynomial corresponding is then
            1+x+y+z+xy+xz+yz+x²+y²+z²
            * This polynomial is represented by the set :
            {
                (0,0,0)
                (1,0,0)
                (0,1,0)
                (0,0,1)
                (1,1,0)
                (1,0,1)
                (0,1,1)
                (2,0,0)
                (0,2,0)
                (0,0,2)
            }

        Calculation of this polynomial could be very long for high orders, so
        it's necessary to compute it once at the initialization.

        """

        polynomial = set()

        # add degree 0
        polynomial.add((0,)*self.in_dim)

        # add degree 1
        first_deg_terms = set()
        for i in range(self.in_dim):
            term = ()
            for j in range(self.in_dim):
                if i==j:
                    term+=(1,)
                else:
                    term+=(0,)
            first_deg_terms.add(term)
        polynomial = polynomial.union(first_deg_terms)

        # add other degrees
        prev_deg_terms = first_deg_terms
        for i in range(self.max_poly_deg-1):
            next_deg_terms = set()
            for prev_term in prev_deg_terms:
                for first_term in first_deg_terms:
                    next_deg_terms.add(add_vectors(prev_term, first_term))
            polynomial = polynomial.union(next_deg_terms)
            prev_deg_terms=next_deg_terms

        list_polynomial = []
        for term in polynomial:
            list_polynomial.append(term)
        list_polynomial.sort()
        self.polynomial = list_polynomial

    def generate_params(self):
        """Generate parameters matrix

        Params is a matrix of size (out_dim, nb_term)
        The initialization range follow the value of self.in_magnitude and
        self.out_magnitude to give a results close to q_home
        """

        # params = []
        # for i in range(self.out_dim):
        #     params.append([])
        #     for term in self.polynomial:
        #         term_deg = sum(i for i in term)
        #         if term_deg == 0:
        #             params[i].append(self.q_home[i])
        #         else:
        #             params[i].append(random.uniform(-1,1)*
        #                 self.random_spread*self.out_magnitude
        #                 /(len(self.polynomial)*self.in_magnitude**term_deg))

        params = []
        P=len(self.polynomial)
        for i in range(self.out_dim):
            params.append([])
            for term in self.polynomial:
                term_deg = sum(i for i in term)
                params[i].append(
                    (self.q_home[i]/P)
                    *(2/self.in_magnitude)**term_deg
                    +random.uniform(
                        -self.random_spread*self.out_magnitude/P,
                        self.random_spread*self.out_magnitude/P
                    )
                )

        self.params = params

    def get_calc_polynomial(self, point):
        """Convert the point in another vector following the calculated
        polynomial
        """

        # According to the python doc, as long as a set is not modified, the
        # iteration order remain the same, which is useful here
        # If there are issue despite this doc info, just convert the set to
        # a list after its creation

        calc_polynomial = []
        for term in self.polynomial:
            calc_term = 1
            for i in range(len(term)):
                calc_term*=point[i]**term[i]
            calc_polynomial.append(calc_term)

        return calc_polynomial

    def compute(self, point):
        """Compute the image of the point in the control space by our current
        function.

        The first step is to calculate a vector containing each term of the
        polynomial.
        Then multiply this vector by the parameters matrix to get the output in
        the control space.
        """

        calc_polynomial = self.get_calc_polynomial(point)

        # Calculate the output vector params*calc_term
        res = []
        for i in range(self.out_dim):
            res_component = 0
            for j in range(len(calc_polynomial)):
                res_component+=self.params[i][j]*calc_polynomial[j]
            res.append(res_component)

        return res

    def update(self, dataset):
        """Update the matrix of parameters.

        For the optimization, using the gradient method on this error function :

        $E(\textbf{M}) = \sum_{t=0}^{D-1} w_t\|\textbf{M}x_t-q_t\|^2$

        Args:
            dataset (list): a list of quadruplet [f(g(x)), g(x), w, x]
        """
        polynomial_dataset = []
        for quadruplet in dataset:
            polynomial_dataset.append([
                self.get_calc_polynomial(quadruplet[0]),
                quadruplet[1],
                quadruplet[2],
                quadruplet[3]
            ])

        next_params = []
        for i in range(self.out_dim):
            next_params.append([])
            for j in range(len(self.polynomial)):
                grad = 0
                for quadruplet in polynomial_dataset:
                    tmp1=0
                    for r in range(len(quadruplet[0])):
                        tmp1+=self.params[i][r]*quadruplet[0][r]

                    grad+=2*quadruplet[2]*quadruplet[0][j]*(tmp1-quadruplet[1][i])

                next_params[i].append(self.params[i][j]-self.alpha*grad)

        self.params = next_params

    def store(self, filename):
        """ Store the current parameters in a file."""
        json_obj = {'params': self.params}
        with open(filename, 'w') as fp:
            json.dump(json_obj, fp)

    def get_nb_term(self, in_dim, max_poly_deg):
        # this is a conjecture
        res = 0
        for i in range(in_dim-1, in_dim-1+max_poly_deg):
            res+=binomial(i, in_dim-1)

        # if not accurate, can use len(self.polynomial)

        return res
