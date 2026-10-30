@extends('layouts.app')

@section('title', 'Absensi')

@section('content')
    <h2>Data Absensi</h2>

    <div class="card shadow-sm">
        <div class="card-body">
            <table class="table table-striped">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Person</th>
                        <th>Gambar</th>
                        <th>Waktu</th>
                    </tr>
                </thead>

                <tbody>
                    @forelse ($data_absensi as $data)
                        <tr>
                            <td>{{ $data->id }}</td>
                            <td>{{ $data->person }}</td>
                            <td>
                                <img
                                    src="{{ route('absensi.gambar', $data->id) }}"
                                    alt="Foto absensi"
                                    width="150"
                                    class="img-thumbnail"
                                >
                            </td>
                            <td>{{ $data->waktu }}</td>
                        </tr>
                    @empty
                        <tr>
                            <td colspan="4" class="text-center">
                                Belum ada data absensi.
                            </td>
                        </tr>
                    @endforelse
                </tbody>
            </table>
        </div>
    </div>
@endsection