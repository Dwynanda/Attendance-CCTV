<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\EncodingData;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;
use Symfony\Component\Process\Process;

class AttendanceController extends Controller
{
    public function dashboard()
    {
        return view('dashboard');
    }

    public function training()
    {
        $data_wajah = EncodingData::all();

        return view('training', compact('data_wajah'));
    }

    public function absensi()
    {
        $data_absensi = DB::table('absensi')
            ->orderByDesc('waktu')
            ->get();

        return view('absensi', compact('data_absensi'));
    }

    public function gambar($id){
        $data = DB::table('absensi')
            ->where('id', $id)
            ->first();

        if (!$data || !$data->img){
            abort(404);
        }

        return response($data->img)
            ->header('Content-Type', 'image/jpeg');
    }

    public function simpan(Request $request){
        $request->validate([
            'name' => 'required|string|max:255',
            'foto' => 'required|image|mimes:jpg,jpeg,png|max:5120'
        ]);

        $foto = $request->file('foto')->store('training');
        $lokasi_foto = Storage::path($foto);

        $process = new Process([
            'python',
            base_path('python/data_training.py'),
            $lokasi_foto,
            $request->name
            ], base_path(),['SYSTEMROOT' => getenv('SYSTEMROOT'), 'PATH' => getenv('PATH')
        ]);

        $process->run();
        Storage::delete($foto);

        if (!$process->isSuccessful()) {
                return redirect()->route('training')
                    ->with('error', $process->getErrorOutput()
                        ?: $process->getOutput());
        }

        return redirect()->route('training')
            ->with('success', 'Data wajah berhasil disimpan!');

    }
}
