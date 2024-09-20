import pandas as pd
import numpy as np
import plotly.graph_objs as go
from scipy.spatial.transform import Rotation as R

df = pd.read_csv("hwc_3d_data.csv") 

#RA and DEC to Cartesian coordinates
def ra_dec_to_cartesian(ra, dec, distance):
    ra_rad = np.deg2rad(ra)
    dec_rad = np.deg2rad(dec)
    x = distance * np.cos(dec_rad) * np.cos(ra_rad)
    y = distance * np.cos(dec_rad) * np.sin(ra_rad)
    z = distance * np.sin(dec_rad)
    return x, y, z


#Generating orbits and apply inclination using a rotation matrix
def generate_orbit(semi_major_axis, inclination, num_points=100):
    angles = np.linspace(0, 2 * np.pi, num_points)
    x_orbit = semi_major_axis * np.cos(angles)
    y_orbit = semi_major_axis * np.sin(angles)
    z_orbit = np.zeros_like(x_orbit)  # Initially in the xy-plane

    # Apply inclination as a rotation around the x-axis
    inclination_rotation = R.from_euler('x', inclination, degrees=True)
    orbit_points = np.vstack((x_orbit, y_orbit, z_orbit)).T
    rotated_orbit = inclination_rotation.apply(orbit_points)

    return rotated_orbit[:, 0], rotated_orbit[:, 1], rotated_orbit[:, 2]


#Generating sphere for habitable zones
def generate_sphere(radius, num_points=100):
    phi = np.linspace(0, np.pi, num_points)
    theta = np.linspace(0, 2 * np.pi, num_points)
    phi, theta = np.meshgrid(phi, theta)
    x = radius * np.sin(phi) * np.cos(theta)
    y = radius * np.sin(phi) * np.sin(theta)
    z = radius * np.cos(phi)
    return x, y, z

def generate_plots(df):
    star_systems = df.groupby('S_NAME')
    plots_html = ""

    for star_name, star_data in star_systems:
        print(f"Creating map for star system: {star_name}")

        # Extract RA, DEC, and distance for the star
        ra = star_data['S_RA'].values[0]
        dec = star_data['S_DEC'].values[0]
        distance = star_data['S_DISTANCE'].values[0]

        # Convert RA, DEC, and distance to Cartesian coordinates for the star
        x_star, y_star, z_star = ra_dec_to_cartesian(ra, dec, distance)

        # Create a trace for the star
        star_trace = go.Scatter3d(
            x=[x_star], y=[y_star], z=[z_star],
            mode='markers',
            marker=dict(size=7, color='yellow'),
            name='Star'
        )

        # Simulating orbits for each exoplanet in its star system
        #further improv needs to be made, 3d modelling of planets and live revolution
        orbit_traces = []
        planet_traces = []
        for _, planet in star_data.iterrows():
            semi_major_axis = planet['P_SEMI_MAJOR_AXIS']
            inclination = planet['P_INCLINATION']

            # Generate the orbit relative to the star's position, apply inclination
            x_orbit, y_orbit, z_orbit = generate_orbit(semi_major_axis, inclination)
            x_orbit += x_star
            y_orbit += y_star
            z_orbit += z_star

            # Create trace for the orbit
            orbit_trace = go.Scatter3d(
                x=x_orbit, y=y_orbit, z=z_orbit,
                mode='lines',
                line=dict(color='blue', width=2),
                name=f'Orbit of {planet["P_NAME"]}'
            )
            orbit_traces.append(orbit_trace)

            # Planet position on the orbit (first point)
            planet_trace = go.Scatter3d(
                x=[x_orbit[0]], y=[y_orbit[0]], z=[z_orbit[0]],
                mode='markers',
                marker=dict(size=3, color='blue'),
                name=planet['P_NAME']
            )
            planet_traces.append(planet_trace)

        # Create the habitable zones
        hz_opt_min = planet['S_HZ_OPT_MIN']
        hz_opt_max = planet['S_HZ_OPT_MAX']
        hz_con_min = planet['S_HZ_CON_MIN']
        hz_con_max = planet['S_HZ_CON_MAX']

        hz_opt_x, hz_opt_y, hz_opt_z = generate_sphere(hz_opt_max)
        hz_con_x, hz_con_y, hz_con_z = generate_sphere(hz_con_max)

        hz_opt_trace = go.Surface(
            x=hz_opt_x + x_star, y=hz_opt_y + y_star, z=hz_opt_z + z_star,
            opacity=0.3,
            colorscale='Greens',
            showscale=False,
            name='Optimistic Habitable Zone'
        )

        hz_con_trace = go.Surface(
            x=hz_con_x + x_star, y=hz_con_y + y_star, z=hz_con_z + z_star,
            opacity=0.3,
            colorscale='Reds',
            showscale=False,
            name='Conservative Habitable Zone'
        )

        # Set up the layout
        layout = go.Layout(
            title=f'Star System: {star_name}',
            scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False),
                bgcolor='black'
            ),
            paper_bgcolor='black',
            plot_bgcolor='black',
        )
        fig = go.Figure(data=[star_trace] + orbit_traces + planet_traces + [hz_opt_trace, hz_con_trace], layout=layout)

        # fig to str
        plots_html += fig.to_html(full_html=False, include_plotlyjs='cdn')

    return plots_html
