class PMF:
    """
     * Probability mass function class
     *
     * @author Dr. James Andrews
     * @version 0.1.0
     * @date 20/01/2023
    """
    def __init__(self, values_list, probabilities_list):
        """
        *  Constructor for objects of class PMF
        *
        * @param  values_list  the values to be sampled
        * @param  probabilities_list  the probabilities to sample the values
        """
        self.values = values_list                # List of integer values
        self.probabilities = probabilities_list  # List of float values

    def get_values(self, index):
        """
        * Get the specific value found at the specified index
        *
        * @param  index  the index of the value to be returned
        * @return    the value at the specified index
        """
        return self.values[index]   # Index is an integer

    def convert_pmf_values_to_cmf(self):
        """
        * Determine the cumulative mass function from the probability mass function
        *
        * @param  pmf  associated probabilities/frequency of occurrence
        * @return  the cumulative mass function for the probability mass function
        """
        # Convert the pmf to a cdf
        cmf_list = [0.0]
        for i in range(len(self.probabilities)):
            cmf_list.extend([cmf_list[i] + self.probabilities[i]])   # Calculate the cumulative
        return cmf_list

    def print_pmf(self):
        """
        * Print the information from the pmf
        *
        """
        print('Value\tProbability')
        for i in range(len(self.probabilities)):
            print(str(self.values[i]) + '\t\t' + str(self.probabilities[i]))
        print()

    def print_cmf(self):
        """
        * Print the information from the cmf
        *
        """
        cmf = self.convert_pmf_values_to_cmf()
        print('Value\tProbability')
        for i in range(len(self.probabilities)+1):
            if i != 0:
                print(str(self.values[i-1]) + '\t\t' + str(cmf[i]))
            else:
                print(str(0) + '\t\t' + str(cmf[i]))
