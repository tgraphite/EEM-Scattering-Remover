import os
import numpy
from matplotlib import pyplot
from numpy.core.fromnumeric import mean
from numpy.core.numeric import count_nonzero
from numpy.lib.npyio import save
import re


class ESR(object):
    def __init__(self, data_input, params):
        self.data_input = data_input
        self.params = params
        matrix_list_form = list()

        if os.path.exists(data_input):
            file_input = open(data_input, 'r')

            for line in file_input:
                line = line.replace('\t', ' ')
                line = line.replace('\n', '')
                line_list_form = line.split(' ')
                matrix_list_form.append(line_list_form)

            file_input.close()

        else:
            print('File not found.')
            nothing = input()
            exit()

        if len(matrix_list_form[0]) == len(matrix_list_form[1]) - 1:
            matrix_list_form[0] = [0.0, ] + matrix_list_form[0]
        elif matrix_list_form[0][0] == '':
            matrix_list_form[0][0] = '0.0'

        matrix = numpy.matrix(matrix_list_form, dtype='float32')
        self.raw_shape = matrix.shape
        self.matrix = matrix[1:, 1:]

        self.excitations = numpy.array(matrix[0, 1:])
        self.emissions = numpy.array(matrix[1:, 0])

    @property
    def removed_matrix(self):
        ray_remove_rad = float(self.params['ray-remove-rad'])
        secray_remove_rad = float(self.params['secray-remove-rad'])
        ram_remove_rad = float(self.params['ram-remove-rad'])
        ram_wavenumber = float(self.params['ram-wavenumber'])

        remove_matrix = numpy.zeros(self.matrix.shape)

        for row_index in range(0, self.matrix.shape[0]):
            for column_index in range(0, self.matrix.shape[1]):
                emission = self.emissions[row_index, 0]
                excitation = self.excitations[0, column_index]

                ref_emission_ray = excitation
                ref_emission_secray = 2 * excitation
                ref_emission_ram = 1.0E7 / \
                    (1.0E7 / excitation - ram_wavenumber)

                if emission < ref_emission_ray + ray_remove_rad and emission > ref_emission_ray - ray_remove_rad:
                    remove = True
                elif emission < ref_emission_secray + secray_remove_rad and emission > ref_emission_secray - secray_remove_rad:
                    remove = True
                elif emission < ref_emission_ram + ram_remove_rad and emission > ref_emission_ram - ram_remove_rad:
                    remove = True
                else:
                    remove = False

                if remove:
                    remove_matrix[row_index,
                                  column_index] = self.matrix[row_index, column_index]

        removed_matrix = self.matrix - remove_matrix
        return removed_matrix

    @property
    def corrected_matrix(self):
        removed_matrix = self.removed_matrix
        relaxation_matrix = numpy.zeros(removed_matrix.shape)
        relax_disp = int(self.params['relaxation-disp'])

        if relax_disp == 0:
            pass

        else:
            for row_index in range(0, removed_matrix.shape[0]):
                for column_index in range(0, removed_matrix.shape[1]):

                    if removed_matrix[row_index, column_index] > 0:
                        continue

                    relaxation = float(0)
                    for row_disp in [relax_disp, -relax_disp]:
                        for column_disp in [relax_disp, -relax_disp]:

                            try:
                                relaxation = relaxation + \
                                    removed_matrix[row_index + row_disp,
                                                   column_index + column_disp]
                            except IndexError:
                                pass

                    relaxation = relaxation / 4.0
                    relaxation_matrix[row_index, column_index] = relaxation

        corrected_matrix = self.removed_matrix + relaxation_matrix

        return corrected_matrix

    # @property
    # def rayleigh_peaks_matrix(self):
    #     width_left = self.params['ray-l']
    #     width_right = self.params['ray-r']

    #     rayleigh_peaks_matrix = numpy.zeros(self.matrix.shape)

    #     for row_index in range(0, self.matrix.shape[0]):
    #         for column_index in range(0, self.matrix.shape[1]):
    #             emission = self.emissions[row_index, 0]
    #             excitation = self.excitations[0, column_index]

    #             ref_emission = excitation
    #             if emission <= ref_emission + width_right and emission >= ref_emission - width_left:
    #                 rayleigh_peaks_matrix[row_index,
    #                                       column_index] = self.matrix[row_index, column_index]

    #     return rayleigh_peaks_matrix

    # @property
    # def raman_peaks_matrix(self):
    #     width_left = self.params['ram-l']
    #     width_right = self.params['ram-r']
    #     wavenumber = self.params['ram-w']

    #     raman_peaks_matrix = numpy.zeros(self.matrix.shape)

    #     for row_index in range(0, self.matrix.shape[0]):
    #         for column_index in range(0, self.matrix.shape[1]):
    #             emission = self.emissions[row_index, 0]
    #             excitation = self.excitations[0, column_index]

    #             ref_emission = 1.0E7 / (1.0E7 / excitation - wavenumber)
    #             if emission <= ref_emission + width_right and emission >= ref_emission - width_left:
    #                 raman_peaks_matrix[row_index,
    #                                    column_index] = self.matrix[row_index, column_index]

    #     return raman_peaks_matrix

    # @property
    # def second_rayleigh_peaks_matrix(self, width_left=10, width_right=10):
    #     width_left = self.params['2ray-l']
    #     width_right = self.params['2ray-r']

    #     second_rayleigh_peaks_matrix = numpy.zeros(self.matrix.shape)

    #     for row_index in range(0, self.matrix.shape[0]):
    #         for column_index in range(0, self.matrix.shape[1]):
    #             emission = self.emissions[row_index, 0]
    #             excitation = self.excitations[0, column_index]

    #             ref_emission = 2 * excitation
    #             if emission <= ref_emission + width_right and emission >= ref_emission - width_left:
    #                 second_rayleigh_peaks_matrix[row_index,
    #                                              column_index] = self.matrix[row_index, column_index]

    #     return second_rayleigh_peaks_matrix

    # @property
    # def all_peaks_matrix(self):
    #     all_peaks_matrix = self.rayleigh_peaks_matrix + \
    #         self.raman_peaks_matrix + self.second_rayleigh_peaks_matrix
    #     return all_peaks_matrix

    # @property
    # def corrected_matrix(self):
    #     corrected_matrix = self.matrix - self.all_peaks_matrix
    #     return corrected_matrix

    def heatmaps(self, maxlevel=150, silent=False):
        title_1 = 'EEM Before Processed'
        title_2 = 'EEM After Scattering Removal'
        title_3 = 'EEM After Relaxation'

        x_label = 'Excitation / nm'
        y_label = 'Emission / nm'

        pyplot.figure(figsize=(10, 8))
        pyplot.xlabel(x_label)
        pyplot.ylabel(y_label)
        pyplot.subplots_adjust(left=0.1, right=0.9, top=0.8)

        level_step = maxlevel / 10
        plot_levels = numpy.arange(0, maxlevel*1.1, level_step)

        pyplot.subplot(1, 3, 1)
        [x, y] = numpy.meshgrid(self.excitations, self.emissions)
        z = self.matrix
        pyplot.contourf(x, y, z, cmap='viridis', levels=plot_levels)
        pyplot.title(title_1)

        pyplot.subplot(1, 3, 2)
        [x, y] = numpy.meshgrid(self.excitations, self.emissions)
        z = self.removed_matrix
        pyplot.contourf(x, y, z, cmap='viridis', levels=plot_levels)
        pyplot.title(title_2)

        pyplot.subplot(1, 3, 3)
        [x, y] = numpy.meshgrid(self.excitations, self.emissions)
        z = self.corrected_matrix
        pyplot.contourf(x, y, z, cmap='viridis', levels=plot_levels)
        pyplot.title(title_3)

        if silent:
            save_name = re.sub(r'\..*', '_esr.png', self.data_input)
            pyplot.savefig(save_name)

        else:
            pyplot.show()

    def save(self):
        single_zero_matrix = numpy.matrix(numpy.zeros((1, 1)))
        header_matrix = numpy.hstack((single_zero_matrix, self.excitations))
        new_matrix = numpy.hstack((self.emissions, self.corrected_matrix))
        new_matrix = numpy.vstack((header_matrix, new_matrix))

        save_name = re.sub(r'\..*', '_corrected.csv', self.data_input)
        numpy.savetxt(save_name, new_matrix, delimiter=',', fmt='%.4f')
        print('Final EEM data saved to {s}'.format(s=save_name))


def read_params(param_file='esr-params.txt'):

    default_params = {
        'ray-remove-rad': 10.0,
        'secray-remove-rad': 12.0,
        'ram-remove-rad': 10.0,
        'ram-wavenumber': 3600.0,
        'relaxation-disp': 2.0,
    }

    params = dict()

    try:
        file = open(param_file, 'r')
        for line in file:
            line_elems = line.split(' ', maxsplit=1)
            param = line_elems[0]
            if param == '#':
                pass
            else:
                value = float(line_elems[1])
                params[param] = value

    except BaseException:
        print('WARING: param file not found or broken, using defaults.')
        params = default_params

    return params


def cli():
    params = read_params()
    print('EEM Scattering Remover. Drag file path into this view.')
    print('The file should be a space-splitted txt file, in which the first row indicates excitations and the first column indicates emissions.')
    print('Edit esr-params.txt to change parameters.')
    params_notification = """
    Using Parameters Below:
        Rayleigh scattering removal radius:     {rayr}
        2nd Ray. scattering removal radius:     {secrayr}
        Raman scattering removal radius:        {ramr}   
        Raman wavenumber:                       {ramw}
        Relaxation radius:                      {relxr}
    """.format(rayr=params['ray-remove-rad'], secrayr=params['secray-remove-rad'], ramr=params['ram-remove-rad'], ramw=params['ram-wavenumber'], relxr=params['relaxation-disp'])
    print(params_notification)

    data_input = input()
    e = ESR(data_input, params)
    e.heatmaps()
    e.save()

# def autorun(data_input):
#     params = read_params()
#     e = ESR(data_input, params)
#     e.heatmaps(silent=True)
#     e.save()


if __name__ == '__main__':
    cli()
