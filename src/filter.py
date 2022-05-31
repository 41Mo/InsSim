def aperiodic_filter(input, output_array, k, T, tau):
    output_array.append(k*tau/(T+tau)*input + 
                            T/(T+tau)*output_array[len(output_array)-1])

def filter(input, T=60):
    k = 1
    tau = 0.01

    result = [input[0]]
    for value in input:
        aperiodic_filter(value, result, k, T, tau)
    del result[0]
    return result
