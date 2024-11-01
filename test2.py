##perfect without relative motion
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from scipy.spatial.transform import Rotation as R

df = pd.read_csv("hwc_3d_data.csv")

planet_images = {
    "TRAPPIST-1 c": "https://github.com/Niharika0804/Exoplanet_Vis_HZ/blob/main/images/Trappist%201%20c.png"
}

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
def generate_sphere(radius, num_points=50):
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

        ra = star_data['S_RA'].values[0]
        dec = star_data['S_DEC'].values[0]
        distance = star_data['S_DISTANCE'].values[0]
        x_star, y_star, z_star = ra_dec_to_cartesian(ra, dec, distance)
        star_radius = star_data['S_RADIUS'].values[0]

        static_traces = []

        star_trace = go.Scatter3d(
            x=[x_star], y=[y_star], z=[z_star],
            mode='markers',
            marker=dict(size=star_radius * 10, color='yellow'),
            name='Star'
        )
        static_traces.append(star_trace)

        orbit_traces = []
        planet_orbits = []
        planet_traces = []  # Added this line
        annotations = []

        for _, planet in star_data.iterrows():
            semi_major_axis = planet['P_SEMI_MAJOR_AXIS']
            inclination = planet['P_INCLINATION']
            planet_radius = planet['P_RADIUS']
            planet_name = planet['P_NAME']

            x_orbit, y_orbit, z_orbit = generate_orbit(semi_major_axis, inclination)
            x_orbit += x_star
            y_orbit += y_star
            z_orbit += z_star

            planet_orbits.append((x_orbit, y_orbit, z_orbit, planet_radius, planet_name))

            orbit_trace = go.Scatter3d(
                x=x_orbit, y=y_orbit, z=z_orbit,
                mode='lines',
                line=dict(
                    #color=f'rgb({np.random.randint(100, 255)},{np.random.randint(100, 255)},{np.random.randint(100, 255)})',
                    color='blue',
                    width=2),
                name=f'Orbit of {planet_name}'
            )
            orbit_traces.append(orbit_trace)

            # Add initial planet position
            planet_trace = go.Scatter3d(
                x=[x_orbit[0]], y=[y_orbit[0]], z=[z_orbit[0]],
                mode='markers',
                marker=dict(size=planet_radius * 10, color='cyan'),
                name=planet_name
            )
            planet_traces.append(planet_trace)

        static_traces.extend(orbit_traces)

        hz_opt_max = star_data['S_HZ_OPT_MAX'].values[0]
        hz_con_max = star_data['S_HZ_CON_MAX'].values[0]

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
        static_traces.extend([hz_opt_trace, hz_con_trace])

        frames = []
        num_frames = len(planet_orbits[0][0])

        for i in range(num_frames):
            frame_data = list(static_traces)
            frame_planets = []

            for x_orbit, y_orbit, z_orbit, planet_radius, planet_name in planet_orbits:
                planet_trace = go.Scatter3d(
                    x=[x_orbit[i]], y=[y_orbit[i]], z=[z_orbit[i]],
                    mode='markers+text',
                    marker=dict(size=planet_radius * 10, color='cyan', symbol='circle'),
                    text=planet_name,
                    textposition="top center",
                    name=planet_name,
                    hovertext=planet_name
                )
                frame_planets.append(planet_trace)

            frame_data.extend(frame_planets)
            frames.append(go.Frame(data=frame_data, name=f'frame_{i}'))

        frames.append(frames[0])

        layout = go.Layout(
            title=f'Star System: {star_name}',
            scene=dict(
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                zaxis=dict(visible=False),
                bgcolor='black',
                aspectmode='data',
                annotations=annotations
            ),
            paper_bgcolor='black',
            plot_bgcolor='black',
            updatemenus=[{
                'buttons': [
                    {'args': [None, {'frame': {'duration': 50, 'redraw': True}, 'fromcurrent': True, 'mode': 'immediate', 'loop': True}],
                     'label': 'Play',
                     'method': 'animate'},
                    {'args': [[None], {'frame': {'duration': 0, 'redraw': True}, 'mode': 'immediate',
                                       'transition': {'duration': 0}}],
                     'label': 'Pause',
                     'method': 'animate'}
                ],
                'type': 'buttons',
                'showactive': False,
                'x': 0.1,
                'y': 0,
                'xanchor': 'right',
                'yanchor': 'top'
            }],
            margin=dict(l=0, r=0, b=0, t=30),
        )

        config = {
            'displayModeBar': True,
            'modeBarButtonsToAdd': ['toggleSpikelines', 'resetViews'],
            'displaylogo': False,
            'scrollZoom': True,
            'showTips': True
        }

        fig = go.Figure(data=static_traces + planet_traces, frames=frames, layout=layout)
        plots_html += fig.to_html(full_html=False, include_plotlyjs='cdn', config=config)
        #print(static_traces)


    return plots_html
