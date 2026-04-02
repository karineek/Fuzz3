Initial error:

```
cirq-core/cirq/contrib/qcircuit/qcircuit_pdf_test.py F                                                                                               [ 72%]
cirq-core/cirq/devices/noise_utils_test.py .....                                                                                                     [ 72%]
cirq-core/cirq/interop/quirk/url_to_circuit_test.py ..................                                                                               [ 72%]
cirq-core/cirq/_import_test.py .                                                                                                                     [ 72%]
cirq-core/cirq/sim/clifford/clifford_simulator_test.py ................................................                                              [ 72%]
cirq-core/cirq/contrib/acquaintance/bipartite_test.py .........................                                                                      [ 72%]
cirq-core/cirq/contrib/qasm_import/_parser_test.py ................................................................................................. [ 73%]
.................................................................................................................................................... [ 74%]
............................................................................................................                                         [ 74%]
cirq-core/cirq/contrib/qcircuit/qcircuit_diagram_info_test.py .                                                                                      [ 74%]
cirq-core/cirq/protocols/act_on_protocol_test.py ......                                                                                              [ 74%]
cirq-core/cirq/protocols/qasm_test.py ...                                                                                                            [ 74%]
cirq-core/cirq/qis/channels_test.py ..........................................................                                                       [ 74%]
cirq-core/cirq/protocols/has_unitary_protocol_test.py .........                                                                                      [ 74%]
cirq-core/cirq/protocols/circuit_diagram_info_protocol_test.py .............                                                                         [ 75%]
cirq-core/cirq/testing/routing_devices_test.py ......                                                                                                [ 75%]
cirq-core/cirq/testing/deprecation_test.py ..                                                                                                        [ 75%]
cirq-core/cirq/ops/state_preparation_channel_test.py ...................                                                                             [ 75%]
cirq-core/cirq/interop/quirk/cells/arithmetic_cells_test.py ..............                                                                           [ 75%]
cirq-core/cirq/value/value_equality_attr_test.py ...........                                                                                         [ 75%]
cirq-core/cirq/testing/equivalent_repr_eval_test.py ...                                                                                              [ 75%]
cirq-core/cirq/value/probability_test.py ......                                                                                                      [ 75%]
cirq-core/cirq/interop/quirk/cells/input_cells_test.py .....                                                                                         [ 75%]
cirq-core/cirq/transformers/dynamical_decoupling_test.py ...............................                                                             [ 75%]
cirq-core/cirq/protocols/mul_protocol_test.py ..                                                                                                     [ 75%]
cirq-core/cirq/contrib/paulistring/recombine_test.py .                                                                                               [ 75%]
cirq-core/cirq/ops/parity_gates_test.py .....................................................                                                        [ 75%]
cirq-core/cirq/ops/permutation_gate_test.py .............                                                                                            [ 75%]
cirq-core/cirq/testing/consistent_act_on_test.py .                                                                                                   [ 75%]
cirq-core/cirq/linalg/diagonalize_test.py .......................................................................................................... [ 76%]
.................................................................................................................................................... [ 77%]
...................................................................                                                                                  [ 77%]
cirq-core/cirq/experiments/random_quantum_circuit_generation_test.py ....................                                                            [ 77%]
cirq-core/cirq/ops/kraus_channel_test.py ..........                                                                                                  [ 77%]
cirq-core/cirq/vis/histogram_test.py ...                                                                                                             [ 77%]
cirq-core/cirq/protocols/trace_distance_bound_test.py .                                                                                              [ 77%]
cirq-core/cirq/vis/state_histogram_test.py .....                                                                                                     [ 77%]
cirq-core/cirq/ops/eigen_gate_test.py ..................................                                                                             [ 77%]
cirq-core/cirq/transformers/gauge_compiling/iswap_gauge_test.py ...........                                                                          [ 77%]
cirq-core/cirq/transformers/analytical_decompositions/clifford_decomposition_test.py .....                                                           [ 77%]
cirq-core/cirq/contrib/qasm_import/qasm_test.py .                                                                                                    [ 77%]
cirq-core/cirq/protocols/apply_channel_protocol_test.py .............                                                                                [ 77%]
cirq-core/cirq/circuits/_box_drawing_character_data_test.py .                                                                                        [ 77%]
cirq-core/cirq/interop/quirk/cells/composite_cell_test.py ..                                                                                         [ 77%]
cirq-core/cirq/value/digits_test.py ....                                                                                                             [ 78%]
cirq-core/cirq/circuits/text_diagram_drawer_test.py ...........                                                                                      [ 78%]
cirq-core/cirq/transformers/gauge_compiling/spin_inversion_gauge_test.py ............................................                                [ 78%]
cirq-core/cirq/interop/quirk/cells/qubit_permutation_cells_test.py .......                                                                           [ 78%]
cirq-core/cirq/transformers/tag_transformers_test.py ......                                                                                          [ 78%]
cirq-core/cirq/transformers/symbolize_test.py ...                                                                                                    [ 78%]
cirq-core/cirq/ops/phased_iswap_gate_test.py ......................................                                                                  [ 78%]
cirq-core/cirq/testing/json_test.py ...                                                                                                              [ 78%]
cirq-core/cirq/ops/projector_test.py ...............                                                                                                 [ 78%]
cirq-core/cirq/experiments/qubit_characterizations_test.py ............................                                                              [ 78%]
cirq-core/cirq/sim/density_matrix_utils_test.py ...............................................                                                      [ 79%]
cirq-core/cirq/transformers/insertion_sort_test.py ......                                                                                            [ 79%]
cirq-core/cirq/ops/phased_x_z_gate_test.py ......................................................................................................... [ 79%]
.................................................................................................................................................... [ 80%]
.................................................................................................................................................... [ 81%]
.................................................................................................................................................... [ 81%]
.................................................................................................................................................... [ 82%]
.................................................................................................................................................... [ 83%]
.............................................................                                                                                        [ 83%]
cirq-core/cirq/contrib/acquaintance/strategies/cubic_test.py .......                                                                                 [ 83%]
cirq-core/cirq/experiments/xeb_fitting_test.py .................................                                                                     [ 83%]
cirq-core/cirq/interop/quirk/cells/input_rotation_cells_test.py .......                                                                              [ 83%]
cirq-core/cirq/sim/clifford/clifford_tableau_simulation_state_test.py ...                                                                            [ 83%]
cirq-core/cirq/transformers/routing/visualize_routed_circuit_test.py ..                                                                              [ 83%]
cirq-core/cirq/contrib/acquaintance/inspection_utils_test.py .............                                                                           [ 83%]
cirq-core/cirq/contrib/paulistring/clifford_target_gateset_test.py .........................                                                         [ 83%]
cirq-core/cirq/ops/identity_test.py ..........................                                                                                       [ 84%]
cirq-core/cirq/protocols/commutes_protocol_test.py ...                                                                                               [ 84%]
cirq-core/cirq/ops/matrix_gates_test.py .............................                                                                                [ 84%]
cirq-core/cirq/contrib/routing/router_test.py .......................                                                                                [ 84%]
cirq-core/cirq/transformers/target_gatesets/cz_gateset_test.py ....................                                                                  [ 84%]
cirq-core/cirq/qis/measures_test.py ...............................................                                                                  [ 84%]
cirq-core/cirq/protocols/json_serialization_test.py x...........x...................x......xx.....x..........x....x..s..................x........... [ 85%]
x..x..............................x.............s............x...............x.x....x...x..............x.............x.x..x...................x....x [ 85%]
..................x..x...............xx..........x.s...x.....x........x...............................x.x..................x....s..x.........sx..x.. [ 86%]
.......x.......x...x....x.......x..............x.................x..s......x........x.x.x.........x............s..............................x.x... [ 87%]
.......x....x..........x.......xx.................x..............s..s........................x..x..................x.....x.........x................ [ 88%]
s.......x......x.....................                                                                                                                [ 88%]
cirq-core/cirq/work/zeros_sampler_test.py ....                                                                                                       [ 88%]
cirq-core/cirq/ops/wait_gate_test.py .........                                                                                                       [ 88%]
cirq-core/cirq/testing/lin_alg_utils_test.py ............................                                                                            [ 88%]
cirq-core/cirq/sim/density_matrix_simulation_state_test.py ........                                                                                  [ 88%]
cirq-core/cirq/value/measurement_key_test.py ..........                                                                                              [ 88%]
cirq-core/cirq/ops/global_phase_op_test.py ..................................                                                                        [ 88%]
cirq-core/cirq/experiments/purity_estimation_test.py .                                                                                               [ 88%]
cirq-core/cirq/testing/circuit_compare_test.py ..................                                                                                    [ 88%]
cirq-core/cirq/protocols/pauli_expansion_protocol_test.py .............                                                                              [ 88%]
cirq-core/cirq/contrib/acquaintance/gates_test.py .................................................................................................. [ 89%]
.......................                                                                                                                              [ 89%]
cirq-core/cirq/devices/named_topologies_test.py ...........................                                                                          [ 89%]
cirq-core/cirq/testing/pytest_utils_test.py ...                                                                                                      [ 89%]
cirq-core/cirq/ops/tags_test.py ..                                                                                                                   [ 89%]
cirq-core/cirq/interop/quirk/cells/measurement_cells_test.py .                                                                                       [ 89%]
cirq-core/cirq/transformers/gauge_compiling/cz_gauge_test.py ...........                                                                             [ 89%]
cirq-core/cirq/value/angle_test.py ...                                                                                                               [ 89%]
cirq-core/cirq/transformers/drop_empty_moments_test.py ..                                                                                            [ 89%]
cirq-core/cirq/linalg/tolerance_test.py ....                                                                                                         [ 89%]
cirq-core/cirq/interop/quirk/cells/unsupported_cells_test.py ..                                                                                      [ 89%]
cirq-core/cirq/qis/noise_utils_test.py ...............                                                                                               [ 89%]
cirq-core/cirq/value/linear_dict_test.py ........................................................................................................... [ 90%]
.........................................................................................                                                            [ 90%]
cirq-core/cirq/transformers/gauge_compiling/sqrt_iswap_gauge_test.py ...........                                                                     [ 90%]
cirq-core/cirq/contrib/quantikz/circuit_to_latex_render_test.py F                                                                                    [ 90%]
cirq-core/cirq/transformers/transformer_api_test.py ..............                                                                                   [ 91%]
cirq-core/cirq/contrib/quimb/density_matrix_test.py .......                                                                                          [ 91%]
cirq-core/cirq/transformers/routing/mapping_manager_test.py ........                                                                                 [ 91%]
cirq-core/cirq/contrib/acquaintance/devices_test.py ..                                                                                               [ 91%]
cirq-core/cirq/ops/pauli_measurement_gate_test.py ...................................                                                                [ 91%]
cirq-core/cirq/ops/op_tree_test.py ......                                                                                                            [ 91%]
cirq-core/cirq/transformers/routing/line_initial_mapper_test.py ...........................                                                          [ 91%]
cirq-core/cirq/transformers/analytical_decompositions/quantum_shannon_decomposition_test.py ...................................................      [ 91%]
cirq-core/cirq/_compat_test.py .................................................                                                                     [ 91%]
cirq-core/cirq/_version_test.py .                                                                                                                    [ 91%]
cirq-core/cirq/contrib/paulistring/separate_test.py .                                                                                                [ 91%]
cirq-core/cirq/testing/consistent_channels_test.py ........                                                                                          [ 91%]
cirq-core/cirq/testing/consistent_protocols_test.py ...                                                                                              [ 91%]
cirq-core/cirq/contrib/acquaintance/strategies/quartic_paired_test.py ...........                                                                    [ 92%]
cirq-core/cirq/transformers/analytical_decompositions/two_qubit_state_preparation_test.py .......................................................... [ 92%]
.................................................................................................................................................... [ 93%]
......................................................                                                                                               [ 93%]
cirq-core/cirq/contrib/routing/swap_network_test.py ....                                                                                             [ 93%]
cirq-core/cirq/ops/classically_controlled_operation_test.py ...............................................................                          [ 93%]
cirq-core/cirq/transformers/analytical_decompositions/two_qubit_to_ms_test.py ............................................                           [ 93%]
cirq-core/cirq/transformers/analytical_decompositions/single_qubit_decompositions_test.py .......................................................... [ 94%]
...............................................                                                                                                      [ 94%]
cirq-core/cirq/experiments/benchmarking/parallel_xeb_test.py .....................                                                                   [ 94%]
cirq-core/cirq/contrib/paulistring/clifford_optimize_test.py .....                                                                                   [ 94%]
cirq-core/cirq/ops/common_gates_test.py ............................................................................................................ [ 95%]
..................................................................................                                                                   [ 95%]
cirq-core/cirq/devices/grid_device_metadata_test.py ........                                                                                         [ 95%]
cirq-core/cirq/sim/mux_test.py .........................                                                                                             [ 95%]
cirq-core/cirq/testing/gate_features_test.py .....                                                                                                   [ 95%]
cirq-core/cirq/ops/gate_operation_test.py .....................................                                                                      [ 95%]
cirq-core/cirq/ops/pauli_sum_exponential_test.py ......................                                                                              [ 95%]
cirq-core/cirq/protocols/equal_up_to_global_phase_protocol_test.py ......                                                                            [ 96%]
cirq-core/cirq/circuits/frozen_circuit_test.py ....                                                                                                  [ 96%]
cirq-core/cirq/transformers/align_test.py ........                                                                                                   [ 96%]
cirq-core/cirq/ops/three_qubit_gates_test.py ........................................                                                                [ 96%]
cirq-core/cirq/interop/quirk/cells/frequency_space_cells_test.py .                                                                                   [ 96%]
cirq-core/cirq/circuits/circuit_test.py ............................................................................................................ [ 96%]
.................................................................................................................................................... [ 97%]
.................................................................................................................................................... [ 98%]
..................................................................                                                                                   [ 98%]
cirq-core/cirq/testing/order_tester_test.py ......                                                                                                   [ 98%]
cirq-core/cirq/value/periodic_value_test.py ....................                                                                                     [ 98%]
cirq-core/cirq/circuits/moment_test.py .................................................                                                             [ 98%]
cirq-core/cirq/transformers/heuristic_decompositions/gate_tabulation_math_utils_test.py ....                                                         [ 99%]
cirq-core/cirq/value/duration_test.py .................                                                                                              [ 99%]
cirq-core/cirq/contrib/graph_device/uniform_graph_device_test.py ......                                                                              [ 99%]
cirq-core/cirq/protocols/control_key_protocol_test.py .                                                                                              [ 99%]
cirq-core/cirq/experiments/z_phase_calibration_test.py .............................                                                                 [ 99%]
cirq-core/cirq/ops/gate_features_test.py ...                                                                                                         [ 99%]
cirq-core/cirq/circuits/circuit_operation_test.py ................................................................................                   [ 99%]
cirq-core/cirq/transformers/gauge_compiling/sqrt_cz_gauge_test.py ......................                                                             [ 99%]
cirq-core/cirq/contrib/svg/svg_test.py ...........                                                                                                   [ 99%]
cirq-core/cirq/circuits/qasm_output_test.py ................................                                                                         [100%]

========================================================================= FAILURES =========================================================================
____________________________________________________________________ test_qcircuit_pdf _____________________________________________________________________

tmp_path = PosixPath('/tmp/pytest-of-ubuntu/pytest-1/test_qcircuit_pdf0')

    def test_qcircuit_pdf(tmp_path: pathlib.Path) -> None:
        circuit = cirq.Circuit(cirq.X(cirq.q(0)), cirq.CZ(cirq.q(0), cirq.q(1)))
>       qcircuit_pdf.circuit_to_pdf_using_qcircuit_via_tex(circuit, f"{tmp_path}/test_file")

cirq-core/cirq/contrib/qcircuit/qcircuit_pdf_test.py:25: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 
cirq-core/cirq/contrib/qcircuit/qcircuit_pdf.py:65: in circuit_to_pdf_using_qcircuit_via_tex
    doc.generate_pdf(filepath, **pdf_kwargs)
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ 

self = Document('default_filepath', [Command('normalsize', Arguments(), Options()), NoEscape(\Qcircuit @R=1em @C=0.75em {
 \\...text{q(0)}}& \qw&\targ \qw&\control \qw    &\qw\\
 &\lstick{\text{q(1)}}& \qw&      \qw&\control \qw\qwx&\qw\\
 \\
})])
filepath = '/tmp/pytest-of-ubuntu/pytest-1/test_qcircuit_pdf0/test_file'

    def generate_pdf(
        self,
        filepath=None,
        *,
        clean=True,
        clean_tex=True,
        compiler=None,
        compiler_args=None,
        silent=True
    ):
        """Generate a pdf file from the document.
    
        Args
        ----
        filepath: str
            The name of the file (without .pdf), if it is `None` the
            ``default_filepath`` attribute will be used.
        clean: bool
            Whether non-pdf files created that are created during compilation
            should be removed.
        clean_tex: bool
            Also remove the generated tex file.
        compiler: `str` or `None`
            The name of the LaTeX compiler to use. If it is None, PyLaTeX will
            choose a fitting one on its own. Starting with ``latexmk`` and then
            ``pdflatex``.
        compiler_args: `list` or `None`
            Extra arguments that should be passed to the LaTeX compiler. If
            this is None it defaults to an empty list.
        silent: bool
            Whether to hide compiler output
        """
    
        if compiler_args is None:
            compiler_args = []
    
        # In case of newer python with the use of the cwd parameter
        # one can avoid to physically change the directory
        # to the destination folder
        python_cwd_available = sys.version_info >= (3, 6)
    
        filepath = self._select_filepath(filepath)
        if not os.path.basename(filepath):
            filepath = os.path.join(os.path.abspath(filepath), "default_basename")
        else:
            filepath = os.path.abspath(filepath)
    
        cur_dir = os.getcwd()
        dest_dir = os.path.dirname(filepath)
    
        if not python_cwd_available:
            os.chdir(dest_dir)
    
        self.generate_tex(filepath)
    
        if compiler is not None:
            compilers = ((compiler, []),)
        else:
            latexmk_args = ["--pdf"]
    
            compilers = (("latexmk", latexmk_args), ("pdflatex", []))
    
        main_arguments = ["--interaction=nonstopmode", filepath + ".tex"]
    
        check_output_kwargs = {}
        if python_cwd_available:
            check_output_kwargs = {"cwd": dest_dir}
    
        os_error = None
    
        for compiler, arguments in compilers:
            command = [compiler] + arguments + compiler_args + main_arguments
    
            try:
                output = subprocess.check_output(
                    command, stderr=subprocess.STDOUT, **check_output_kwargs
                )
            except (OSError, IOError) as e:
                # Use FileNotFoundError when python 2 is dropped
                os_error = e
    
                if os_error.errno == errno.ENOENT:
                    # If compiler does not exist, try next in the list
                    continue
                raise
            except subprocess.CalledProcessError as e:
                # For all other errors print the output and raise the error
                print(e.output.decode())
                raise
            else:
                if not silent:
                    print(output.decode())
    
            if clean:
                try:
                    # Try latexmk cleaning first
                    subprocess.check_output(
                        ["latexmk", "-c", filepath],
                        stderr=subprocess.STDOUT,
                        **check_output_kwargs
                    )
                except (OSError, IOError, subprocess.CalledProcessError):
                    # Otherwise just remove some file extensions.
                    extensions = ["aux", "log", "out", "fls", "fdb_latexmk"]
    
                    for ext in extensions:
                        try:
                            os.remove(filepath + "." + ext)
                        except (OSError, IOError) as e:
                            # Use FileNotFoundError when python 2 is dropped
                            if e.errno != errno.ENOENT:
                                raise
                rm_temp_dir()
    
            if clean_tex:
                os.remove(filepath + ".tex")  # Remove generated tex file
    
            # Compilation has finished, so no further compilers have to be
            # tried
            break
    
        else:
            # Notify user that none of the compilers worked.
>           raise (
                CompilerError(
                    "No LaTex compiler was found\n"
                    "Either specify a LaTex compiler "
                    "or make sure you have latexmk or pdfLaTex installed."
                )
            )
E           pylatex.errors.CompilerError: No LaTex compiler was found
E           Either specify a LaTex compiler or make sure you have latexmk or pdfLaTex installed.

.venv/lib/python3.11/site-packages/pylatex/document.py:325: CompilerError
___________________________________________________________________ test_render_circuit ____________________________________________________________________

tmp_path = PosixPath('/tmp/pytest-of-ubuntu/pytest-1/test_render_circuit0')

    def test_render_circuit(tmp_path: pathlib.Path) -> None:
        q0, q1 = cirq.LineQubit.range(2)
        circuit = cirq.Circuit(
            cirq.H(q0),
            cirq.CNOT(q0, q1),
            cirq.rx(0.25 * np.pi).on(q1),
            cirq.measure(q0, q1, key='result'),
        )
        # Render and display in Jupyter (if available), also save to a file
        img_or_path = render_circuit(
            circuit,
            output_png_path=tmp_path / "my_circuit.png",
            output_tex_path=tmp_path / "my_circuit.tex",
            output_pdf_path=tmp_path / "my_circuit.pdf",
            fold_at=2,
            debug=True,
            wire_labels="qid",
        )
>       assert img_or_path is not None
E       assert None is not None

cirq-core/cirq/contrib/quantikz/circuit_to_latex_render_test.py:41: AssertionError
------------------------------------------------------------------- Captured stdout call -------------------------------------------------------------------
[Debug] Temporary directory created at: /tmp/tmpcthpbvrh
[Debug] Generating LaTeX source...
[Debug] Generated LaTeX (first 500 chars):
 \documentclass[preview, border=2pt]{standalone}
% Core drawing packages
\usepackage{tikz}
\usetikzlibrary{quantikz} % Loads the quantikz library (latest installed version)
% Optional useful TikZ libraries
\usetikzlibrary{fit, arrows.meta, decorations.pathreplacing, calligraphy}
% Font encoding and common math packages
\usepackage[T1]{fontenc}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{amssymb}
% --- Custom Preamble Injection Point ---
% --- End Custom Preamble ---
\begin{document}
\b...
[Debug] LaTeX saved to temporary file: /tmp/tmpcthpbvrh/circuit_render.tex
[Debug] Running pdflatex (/usr/bin/pdflatex)...
[Debug]   pdflatex run 1/2...
!!! pdflatex failed on run 1 (exit code 1) !!!
--- Tail of circuit_render.log ---
This is pdfTeX, Version 3.14159265-2.6-1.40.20 (TeX Live 2019/Debian) (preloaded format=pdflatex 2024.3.18)  31 MAR 2026 00:16
entering extended mode
 restricted \write18 enabled.
 %&-line parsing enabled.
**/tmp/tmpcthpbvrh/circuit_render.tex
(/tmp/tmpcthpbvrh/circuit_render.tex
LaTeX2e <2020-02-02> patch level 2
L3 programming layer <2020-02-14>

! LaTeX Error: File `standalone.cls' not found.

Type X to quit or <RETURN> to proceed,
or enter new name. (Default extension: cls)

Enter file name: 
! Emergency stop.
<read *> 
         
l.3 \usepackage
               {tikz}^^M 
Here is how much of TeX's memory you used:
 23 strings out of 483183
 566 string characters out of 5966292
 231602 words of memory out of 5000000
 15137 multiletter control sequences out of 15000+600000
 532338 words of font info for 24 fonts, out of 8000000 for 9000
 14 hyphenation exceptions out of 8191
 14i,0n,17p,114b,10s stack positions out of 5000i,500n,10000p,200000b,80000s

!  ==> Fatal error occurred, no output PDF file produced!

===================================================================== warnings summary =====================================================================
cirq-core/cirq/work/observable_measurement_data_test.py::test_bitstring_accumulator_errors
  /home/ubuntu/Cirq/.venv/lib/python3.11/site-packages/numpy/_core/fromnumeric.py:4232: RuntimeWarning: Degrees of freedom <= 0 for slice
    return _methods._var(a, axis=axis, dtype=dtype, out=out, ddof=ddof,

cirq-core/cirq/work/observable_measurement_data_test.py::test_bitstring_accumulator_errors
  /home/ubuntu/Cirq/.venv/lib/python3.11/site-packages/numpy/_core/_methods.py:211: RuntimeWarning: invalid value encountered in scalar divide
    ret = ret.dtype.type(ret / rcount)

cirq-core/cirq/contrib/quantikz/circuit_to_latex_quantikz_test.py::test_misc_gates
  /home/ubuntu/Cirq/cirq-core/cirq/contrib/quantikz/circuit_to_latex_quantikz.py:589: UserWarning: Op -1 no qubits.
    warnings.warn(f"Op {op} no qubits.")

cirq-core/cirq/ops/dense_pauli_string_test.py::test_protocols
cirq-core/cirq/ops/controlled_gate_test.py::test_controlled_gate_is_consistent[gate16-False]
cirq-core/cirq/ops/global_phase_op_test.py::test_protocols
  /home/ubuntu/Cirq/cirq-core/cirq/study/resolver.py:194: RuntimeWarning: divide by zero encountered in float_power
    return np.float_power(cast(complex, base), cast(complex, exponent))

cirq-core/cirq/experiments/t1_decay_experiment_test.py::test_plot_does_not_raise_error
cirq-core/cirq/experiments/t1_decay_experiment_test.py::test_plot_does_not_raise_error
  /home/ubuntu/Cirq/cirq-core/cirq/experiments/t1_decay_experiment.py:142: OptimizeWarning: Covariance of the parameters could not be estimated
    self.popt, _ = optimize.curve_fit(exp_decay, xs, probs, p0=[t1_guess, 1.0, 0.0])

cirq-core/cirq/experiments/t1_decay_experiment_test.py::test_curve_fit_plot_works
  /home/ubuntu/Cirq/cirq-core/cirq/experiments/t1_decay_experiment.py:146: RuntimeWarning: Optimal parameters could not be found for curve fit
    warnings.warn("Optimal parameters could not be found for curve fit", RuntimeWarning)

cirq-core/cirq/sim/state_vector_simulator_test.py::test_state_vector_trial_result_equality
  /home/ubuntu/Cirq/cirq-core/cirq/sim/state_vector_simulator.py:135: UserWarning: final state vector's norm=np.float32(0.0) is too far from 1, 1.0 > 0.0003452669770922512.skipping renormalization
    warnings.warn(

cirq-core/cirq/experiments/single_qubit_readout_calibration_test.py::test_estimate_parallel_readout_errors_no_noise
  /home/ubuntu/Cirq/cirq-core/cirq/vis/histogram.py:123: UserWarning: Data has no positive values, and therefore cannot be log-scaled.
    set_semilog()

cirq-core/cirq/experiments/single_qubit_readout_calibration_test.py::test_estimate_parallel_readout_errors_no_noise
  /home/ubuntu/Cirq/cirq-core/cirq/vis/histogram.py:124: UserWarning: Data has no positive values, and therefore cannot be log-scaled.
    set_lim(0, 1)

cirq-core/cirq/experiments/qubit_characterizations_test.py::test_single_qubit_randomized_benchmarking
  /home/ubuntu/Cirq/cirq-core/cirq/experiments/qubit_characterizations_test.py:117: DeprecationWarning: single_qubit_randomized_benchmarking was used but is deprecated.
  It will be removed in cirq v2.0.
  please use single_qubit_rb instead
  
    results = single_qubit_randomized_benchmarking(simulator, qubit, num_clifford_range=num_cfds)

cirq-core/cirq/experiments/qubit_characterizations_test.py::test_parallel_single_qubit_parallel_single_qubit_randomized_benchmarking
  /home/ubuntu/Cirq/cirq-core/cirq/experiments/qubit_characterizations_test.py:130: DeprecationWarning: parallel_single_qubit_randomized_benchmarking was used but is deprecated.
  It will be removed in cirq v2.0.
  please use parallel_single_qubit_rb instead
  
    results = parallel_single_qubit_randomized_benchmarking(

cirq-core/cirq/experiments/qubit_characterizations_test.py::test_parallel_single_qubit_parallel_single_qubit_randomized_benchmarking
cirq-core/cirq/experiments/qubit_characterizations_test.py::test_parallel_single_qubit_randomized_benchmarking_with_noise
  /home/ubuntu/Cirq/cirq-core/cirq/experiments/qubit_characterizations.py:158: OptimizeWarning: Covariance of the parameters could not be estimated
    return curve_fit(

cirq-core/cirq/experiments/qubit_characterizations_test.py::test_parallel_single_qubit_randomized_benchmarking_with_noise
  /home/ubuntu/Cirq/cirq-core/cirq/experiments/qubit_characterizations_test.py:148: DeprecationWarning: parallel_single_qubit_randomized_benchmarking was used but is deprecated.
  It will be removed in cirq v2.0.
  please use parallel_single_qubit_rb instead
  
    results = parallel_single_qubit_randomized_benchmarking(

cirq-core/cirq/contrib/quantikz/circuit_to_latex_render_test.py::test_render_circuit
  /home/ubuntu/Cirq/cirq-core/cirq/contrib/quantikz/circuit_to_latex_render.py:211: UserWarning: 'pdftoppm' not found. Cannot convert PDF to PNG. This tool is part of the Poppler utilities. On Ubuntu/Debian: `sudo apt-get install poppler-utils`. On macOS: `brew install poppler`. On Windows: Download Poppler for Windows (e.g., from Poppler for Windows GitHub releases) and add its `bin` directory to your system PATH.
    warnings.warn(

cirq-core/cirq/experiments/z_phase_calibration_test.py::test_calibrate_z_phases_workflow_no_options[angles2-error2]
cirq-core/cirq/experiments/z_phase_calibration_test.py::test_calibrate_z_phases_workflow_no_options[angles1-error1]
  /home/ubuntu/Cirq/cirq-core/cirq/experiments/xeb_fitting.py:659: OptimizeWarning: Covariance of the parameters could not be estimated
    (a, layer_fid), pcov = optimize.curve_fit(

cirq-core/cirq/circuits/qasm_output_test.py::test_qasm_global_phase
  /home/ubuntu/Cirq/cirq-core/cirq/ops/gate_operation.py:341: UserWarning: OpenQASM 2.0 does not support global phase.Since the global phase does not affect the measurement results, the conversion to QASM is disregarded.
    warnings.warn(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================================================================= short test summary info ==================================================================
FAILED cirq-core/cirq/contrib/qcircuit/qcircuit_pdf_test.py::test_qcircuit_pdf - pylatex.errors.CompilerError: No LaTex compiler was found
FAILED cirq-core/cirq/contrib/quantikz/circuit_to_latex_render_test.py::test_render_circuit - assert None is not None
===================================== 2 failed, 20025 passed, 10 skipped, 64 xfailed, 21 warnings in 287.81s (0:04:47) ====================================
```

