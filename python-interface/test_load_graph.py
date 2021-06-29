"""
test_load_graph.py

Contains methods for loading a HIRAX-style graph, timing, then setting up connections.


(Temporary) Naming scheme:
 - COR######: Correlator input
 - ANT######: Antenna
 - DPF######: Dual-Polarization Feed
 - BLN######: (Active) Balun
 - RFT######: RFoF transmitter
 - OPF######: Optical Fiber
 - RFR######: RFoF receiver
 - ADC######: Analog-to-Digital converter


Anatoly Zavyalov, 2021
"""

from graph_interface import GraphInterface
from gremlin_python.driver.protocol import GremlinServerError

from datetime import datetime

import matplotlib.pyplot as plt

import logging


def clear_graph(gi: GraphInterface) -> None:
    """

    Clear the graph stored in the graph traversal of the GraphInterface.

    # TODO: THIS FUNCTION IS FOR TESTING PURPOSES ONLY. 

    :param gi: The GraphInterface containing a graph.
    :type gi: GraphInterface
    """

    logging.warn("Dropping all vertices!")

    success = False
    while not success:
        
        try:
            gi.g.V().drop().iterate()
            success = True

        except GremlinServerError as e:
            logging.warn(f"Error while trying to drop all vertices. {e}")

    

def load_graph(dishes: int, connections: list) -> GraphInterface:
    """

    Instantiate a GraphInterface, and set up a HIRAX-style graph with 
    :param dishes: dishes with each pair of components in the 
    signal chain being connected and disconnected identically 
    based on :param connections:.

    :param dishes: Number of dishes the graph will contain.
    :type dishes: int
    :param connections: A list of (float, bool) 2-tuples, where the first 
    element is the time and the second element is whether a connection was 
    started or stopped at that time. List must be sorted by time, 
    and each second element must alternate.
    :type connections: list
    :return: A GraphInterface instance containing the 
    graph traversal to the instantiated graph.
    :rtype: GraphInterface
    """

    gi = GraphInterface()

    # Clear entire graph.
    clear_graph(gi)

    # Correlator node name
    cor = 'COR000000'

    # Set up the types
    types = ['COR', 'ANT', 'DPF', 'BLN', 'RFT', 'OPF', 'RFR', 'ADC']

    total = 0

    now = datetime.now()

    for t in types:
        gi.add_type(t)

    # Add a correlator input node
    gi.add_component(cor)
    gi.set_type(cor, 'COR')

    total += (datetime.now() - now).total_seconds()

    # Add the components and connect them at different times.
    for i in range(1, dishes + 1):

        # The names of the components to refer to
        ant = f'ANT{str(i).zfill(6)}'
        dpf = f'DPF{str(i).zfill(6)}'
        bln = (f'BLN{str(2 * i - 1).zfill(6)}', f'BLN{str(2 * i).zfill(6)}')
        rft = (f'RFT{str(2 * i - 1).zfill(6)}', f'RFT{str(2 * i).zfill(6)}')
        opf = (f'OPF{str(2 * i - 1).zfill(6)}', f'OPF{str(2 * i).zfill(6)}')
        rfr = (f'RFR{str(2 * i - 1).zfill(6)}', f'RFR{str(2 * i).zfill(6)}')
        adc = (f'ADC{str(2 * i - 1).zfill(6)}', f'ADC{str(2 * i).zfill(6)}')

        now = datetime.now()

        gi.add_component(ant)
        gi.add_component(dpf)

        gi.set_type(ant, 'ANT')
        gi.set_type(dpf, 'DPF')

        for ind in (0, 1):
            gi.add_component(bln[ind])
            gi.add_component(rft[ind])
            gi.add_component(opf[ind])
            gi.add_component(rfr[ind])
            gi.add_component(adc[ind])

            gi.set_type(bln[ind], 'BLN')
            gi.set_type(rft[ind], 'RFT')
            gi.set_type(opf[ind], 'OPF')
            gi.set_type(rfr[ind], 'RFR')
            gi.set_type(adc[ind], 'ADC')

        for (time, connection) in connections:

            gi.set_connection(name1=ant, name2=dpf, 
                time=time, connection=connection)

            for ind in (0, 1):

                # Pairs of names to connect
                pairs = [(ant, dpf), (dpf, bln[ind]), (bln[ind], rft[ind]), 
                    (rft[ind], opf[ind]), (opf[ind], rfr[ind]), 
                    (rfr[ind], adc[ind]), (adc[ind], cor)]

                for pair in pairs:
                    gi.set_connection(name1=pair[0], name2=pair[1], 
                        time=time, connection=connection)

        delta = (datetime.now() - now).total_seconds()

        total += delta

        logging.info(f"Adding dish {i} done, took {delta} seconds.")
    
    logging.info(f"Graph with {dishes} dishes loaded, "
        + f"took {total} total seconds.")

    return gi


def load_graph_v2(dishes: int, mod: int) -> GraphInterface:
    """

    Instantiate a GraphInterface, and set up a HIRAX-style graph with 
    :param dishes: all dish signal chains connected at dish# % :param mod:, 
    disconnected at dish# % :param mod: + 1

    :param dishes: Number of dishes the graph will contain.
    :type dishes: int
    :param mod: What to modulo each time of dish signal chain connectedness by
    :type mod: int
    :return: A GraphInterface instance containing the 
    graph traversal to the instantiated graph.
    :rtype: GraphInterface
    """

    gi = GraphInterface()

    # Clear entire graph.
    clear_graph(gi)

    # Correlator node name
    cor = 'COR000000'

    # Set up the types
    types = ['COR', 'ANT', 'DPF', 'BLN', 'RFT', 'OPF', 'RFR', 'ADC']

    total = 0

    now = datetime.now()

    for t in types:
        gi.add_type(t)

    # Add a correlator input node
    gi.add_component(cor)
    gi.set_type(cor, 'COR')

    total += (datetime.now() - now).total_seconds()

    # Add the components and connect them at different times.
    for i in range(1, dishes + 1):

        # The names of the components to refer to
        ant = f'ANT{str(i).zfill(6)}'
        dpf = f'DPF{str(i).zfill(6)}'
        bln = (f'BLN{str(2 * i - 1).zfill(6)}', f'BLN{str(2 * i).zfill(6)}')
        rft = (f'RFT{str(2 * i - 1).zfill(6)}', f'RFT{str(2 * i).zfill(6)}')
        opf = (f'OPF{str(2 * i - 1).zfill(6)}', f'OPF{str(2 * i).zfill(6)}')
        rfr = (f'RFR{str(2 * i - 1).zfill(6)}', f'RFR{str(2 * i).zfill(6)}')
        adc = (f'ADC{str(2 * i - 1).zfill(6)}', f'ADC{str(2 * i).zfill(6)}')

        now = datetime.now()

        gi.add_component(ant)
        gi.add_component(dpf)

        gi.set_type(ant, 'ANT')
        gi.set_type(dpf, 'DPF')

        for ind in (0, 1):
            gi.add_component(bln[ind])
            gi.add_component(rft[ind])
            gi.add_component(opf[ind])
            gi.add_component(rfr[ind])
            gi.add_component(adc[ind])

            gi.set_type(bln[ind], 'BLN')
            gi.set_type(rft[ind], 'RFT')
            gi.set_type(opf[ind], 'OPF')
            gi.set_type(rfr[ind], 'RFR')
            gi.set_type(adc[ind], 'ADC')

        
        connections = [(i % mod, True), (i % mod + 1, False)]

        for (time, connection) in connections:

            gi.set_connection(name1=ant, name2=dpf, 
                time=time, connection=connection)

            for ind in (0, 1):

                # Pairs of names to connect
                pairs = [(ant, dpf), (dpf, bln[ind]), (bln[ind], rft[ind]), 
                (rft[ind], opf[ind]), (opf[ind], rfr[ind]), 
                (rfr[ind], adc[ind]), (adc[ind], cor)]

                for pair in pairs:
                    gi.set_connection(name1=pair[0], name2=pair[1], 
                        time=time, connection=connection)

        delta = (datetime.now() - now).total_seconds()

        total += delta

        logging.info(f"Adding dish {i} done, took {delta} seconds.")
    
    logging.info(f"Graph with {dishes} dishes loaded, "
        + f"took {total} total seconds.")

    return gi


def load_graph_increment(dishes: int, 
    skip_creation: bool=False) -> GraphInterface:
    """

    Instantiate a GraphInterface, and set up a HIRAX-style graph with 
    :param dishes: all dish signal chains connected at 
    dish# and never disconnected.

    :param dishes: Number of dishes the graph will contain.
    :type dishes: int
    :param skip_creation: Whether to skip creation of the graph 
    if it already exists, defaults to False
    :type skip_creation: bool
    :return: A GraphInterface instance containing the 
    graph traversal to the instantiated graph.
    :rtype: GraphInterface
    """

    gi = GraphInterface()

    if not skip_creation:

        # Clear entire graph.
        clear_graph(gi)

        # Correlator node name
        cor = 'COR000000'

        # Set up the types
        types = ['COR', 'ANT', 'DPF', 'BLN', 'RFT', 'OPF', 'RFR', 'ADC']

        total = 0

        now = datetime.now()

        for t in types:
            gi.add_type(t)

        # Add a correlator input node
        gi.add_component(cor)
        gi.set_type(cor, 'COR')

        total += (datetime.now() - now).total_seconds()

        # Add the components and connect them at different times.
        for i in range(1, dishes + 1):

            # The names of the components to refer to
            ant = f'ANT{str(i).zfill(6)}'
            dpf = f'DPF{str(i).zfill(6)}'
            bln = (f'BLN{str(2 * i - 1).zfill(6)}', f'BLN{str(2 * i).zfill(6)}')
            rft = (f'RFT{str(2 * i - 1).zfill(6)}', f'RFT{str(2 * i).zfill(6)}')
            opf = (f'OPF{str(2 * i - 1).zfill(6)}', f'OPF{str(2 * i).zfill(6)}')
            rfr = (f'RFR{str(2 * i - 1).zfill(6)}', f'RFR{str(2 * i).zfill(6)}')
            adc = (f'ADC{str(2 * i - 1).zfill(6)}', f'ADC{str(2 * i).zfill(6)}')

            now = datetime.now()

            gi.add_component(ant)
            gi.add_component(dpf)

            gi.set_type(ant, 'ANT')
            gi.set_type(dpf, 'DPF')

            for ind in (0, 1):
                gi.add_component(bln[ind])
                gi.add_component(rft[ind])
                gi.add_component(opf[ind])
                gi.add_component(rfr[ind])
                gi.add_component(adc[ind])

                gi.set_type(bln[ind], 'BLN')
                gi.set_type(rft[ind], 'RFT')
                gi.set_type(opf[ind], 'OPF')
                gi.set_type(rfr[ind], 'RFR')
                gi.set_type(adc[ind], 'ADC')

            
            connections = [(i, True)]

            for (time, connection) in connections:

                gi.set_connection(name1=ant, name2=dpf, 
                    time=time, connection=connection)

                for ind in (0, 1):

                    # Pairs of names to connect
                    pairs = [(ant, dpf), (dpf, bln[ind]), (bln[ind], rft[ind]), 
                        (rft[ind], opf[ind]), (opf[ind], rfr[ind]), 
                        (rfr[ind], adc[ind]), (adc[ind], cor)]

                    for pair in pairs:
                        gi.set_connection(name1=pair[0], name2=pair[1], 
                            time=time, connection=connection)

            delta = (datetime.now() - now).total_seconds()

            total += delta

            logging.info(f"Adding dish {i} done, took {delta} seconds.")
        
        logging.info(f"Graph with {dishes} dishes loaded, "
            +f"took {total} total seconds.")

    return gi


def benchmark_paths(time: int, dishes: int, mod: int) -> None:
    """Run a benchmark performing path queries on the entire graph stored in 
    GraphInterface and an igraph.Graph LocalGraph, and compare the two.

    :param time: Time to which to query the graph at.
    :type time: int
    :param dishes: Number of dishes
    :type dishes: int
    :param mod: Number to modulo by in order to 
    have the times of the dishes repeat.
    :type mod: int
    """

    logging.info(f"Benchmark: Started benchmark with {dishes} dishes, "
        + f"modulo of {mod} and at time {time}.")

    gi = load_graph_v2(dishes=dishes, mod=mod)

    now = datetime.now()

    pairs = gi.get_connected_vertices_at_time(time)

    gi.local_graph.create_from_connections_undirected(pairs)

    subgraph_load_time = (datetime.now() - now).total_seconds()

   

    # the numbers of the dishes to test.
    dishes_to_test = [time + i for i in range(0, dishes, mod)]

    times1 = []

    times2 = []

    for d in dishes_to_test:
        ant = f'ANT{str(d).zfill(6)}'

        now = datetime.now()

        gi.find_paths(name1=ant, name2='COR000000', avoid_type='', time=time)

        times1.append((datetime.now() - now).total_seconds())

        now = datetime.now()

        gi.local_graph.find_shortest_paths(name1=ant, name2='COR000000')

        times2.append((datetime.now() - now).total_seconds())

    plt.plot(dishes_to_test, times1, label="Entire Graph")
    plt.plot(dishes_to_test, times2, label="igraph Subgraph")
    plt.title(f"{dishes} dishes, time {time}, modulo {mod}")
    plt.xlabel("Dish number")
    plt.ylabel("Query Time (s)")
    plt.legend()
    plt.savefig('benchmark_plot.png')

    logging.info(f"Benchmark: entire graph query times: {times1}")
    logging.info(f"Benchmark: Making subgraph took \
        {subgraph_load_time} seconds.")
    logging.info(f"Benchmark: subgraph query times: {times2}")

    logging.info(f"Benchmark: total for entire graph: {sum(times1)} seconds.")
    logging.info(f"Benchmark: total for subgraph: "
        + f"{sum(times2)} + {subgraph_load_time} = "
        + f"{sum(times2) + subgraph_load_time} seconds.")

    logging.info(f"Benchmark: Finished benchmark with {dishes} dishes, "
        + f"modulo of {mod} and at time {time}.")

    # gi.local_graph.visualize_graph('subgraph.pdf')

    # gi.export_graph('test_load_graph.xml')


def benchmark_increment(dishes: int, step: int, 
    skip_creation: bool=False) -> None:
    """Run a benchmark performing path queries on the entire graph stored 
    in GraphInterface and an igraph.Graph LocalGraph, and compare the two.

    :param dishes: Number of dishes
    :type dishes: int
    :param step: Incrementation of the time to query the graph at.
    :type step: int
    :param skip_creation: Whether to skip creation of the graph if 
    it already exists, defaults to False
    :type skip_creation: bool
    """

    logging.info(f"Benchmark: Started incremental benchmark "
        + f"with {dishes} dishes, step of {step}.")

    gi = load_graph_increment(dishes=dishes, skip_creation=skip_creation)

    times_bruteforce = []

    times_subgraph = []

    times_subgraph_query = []

    times_subgraph_setup = []

    for time in range(1, dishes + 1, step):
        
        logging.info(f"Benchmark: Now looking at time {time}.")

        total_bruteforce, total_subgraph = 0, 0

        now = datetime.now()

        vertices_iter, edges_iter = gi.get_subgraph_iterators(time)

        query_time = (datetime.now() - now).total_seconds()

        times_subgraph_query.append(query_time)

        now = datetime.now()

        times = gi.local_graph \
            .create_from_connections_undirected(
                vertices_iter, edges_iter
        )

        total_subgraph += (datetime.now() - now).total_seconds() + query_time

        times_subgraph_setup.append(times)

        dishes_to_test = list(range(1, time + 1))

        for d in dishes_to_test:
            ant = f'ANT{str(d).zfill(6)}'

            now = datetime.now()

            gi.find_shortest_path(name1=ant, name2='COR000000', 
                avoid_type='', time=time)

            total_bruteforce += (datetime.now() - now).total_seconds()

            now = datetime.now()

            gi.local_graph.find_shortest_paths(name1=ant, name2='COR000000')

            total_subgraph += (datetime.now() - now).total_seconds()

        times_bruteforce.append(total_bruteforce)

        times_subgraph.append(total_subgraph)
    

    plt.plot(list(range(1, dishes + 1, step)), times_subgraph, label="Subgraph")
    plt.plot(list(range(1, dishes + 1, step)), 
        times_bruteforce, label="Direct DB")
    plt.title(f"{dishes} dishes, step of {step}")
    plt.xlabel("Number of dishes")
    plt.ylabel("Query Time (s)")
    plt.legend()
    plt.grid(True)
    plt.savefig('benchmark_plot.png')

    logging.info(f"Benchmark: entire graph query times: {times_bruteforce}")
    logging.info(f"Benchmark: total subgraph times: {times_subgraph}")
    logging.info(f"Benchmark: subgraph query times: {times_subgraph_query}")

    logging.info(f"Benchmark: subgraph local "
        + f"creation times: {times_subgraph_setup}")

    logging.info(f"Benchmark: total for entire graph: "
        + f"{sum(times_bruteforce)} seconds.")

    logging.info(f"Benchmark: total for subgraph: "
        + f"{sum(times_subgraph)} seconds.")

    logging.info(f"Benchmark: Finished incremental benchmark with "
        + f"{dishes} dishes and step of {step}. See saved plot.")

    # gi.local_graph.visualize_graph('subgraph.pdf')

    # gi.export_graph('test_load_graph.xml')


def visualize_subgraph_at_time(time: float, 
        location: str='subgraph.pdf') -> None:
    """
    Visualize the subgraph at some time :param time:.


    :param time: The time to visualize the subgraph at.
    :type time: float

    :param location: Where to save the subgraph at, defaults to subgraph.pdf
    :type location: str
    """

    gi = GraphInterface()

    vertices_iter, edges_iter = gi.get_subgraph_iterators(time)

    gi.local_graph.create_from_connections_undirected(
            vertices_iter, edges_iter
    )

    gi.local_graph.visualize_graph(location)


if __name__ == "__main__":
    
    # benchmark_subgraph_queries(dishes=1024, step=32, skip_creation=False)

    logging.basicConfig(filename='interface.log', level=logging.INFO)

    benchmark_increment(dishes=1024, step=32, skip_creation=True)

    # visualize_subgraph_at_time(5)

    

        

