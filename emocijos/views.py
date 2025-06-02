from django.shortcuts import render, redirect
from django.templatetags.static import static
import random
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Emocijų sąrašas (9 images)
paveiksleliai = [
    ('image/lietutis.png', 'liūdnas'),
    ('image/zaisliukas.png', 'liūdnas'),
    ('image/dziugutis.png', 'linksmas'),
    ('image/pikciurna.png', 'piktas'),
    ('image/batut.png', 'linksmas'),
    ('image/netikėtumas.png', 'nustebęs'),
    ('image/dovanuška.png', 'linksmas'),
    ('image/mylumylu.png', 'linksmas'),
    ('image/balionėlis.png', 'linksmas')
]

def emociju_atpazinimas(request):
    # Initialize session if not already set
    if 'rodyti_paveikslelius' not in request.session:
        # Group images by emotion
        emotions = {'liūdnas': [], 'linksmas': [], 'piktas': [], 'nustebęs': []}
        for img, emo in paveiksleliai:
            emotions[emo].append(img)
        
        # Select 8 images: 2 per emotion (duplicate where needed)
        rodyti_paveikslelius = []
        try:
            if emotions['linksmas']:
                rodyti_paveikslelius.extend([(img, 'linksmas') for img in random.sample(emotions['linksmas'], min(2, len(emotions['linksmas'])))])
            if emotions['liūdnas']:
                rodyti_paveikslelius.extend([(img, 'liūdnas') for img in random.sample(emotions['liūdnas'], min(2, len(emotions['liūdnas'])))])
            if emotions['piktas']:
                rodyti_paveikslelius.extend([(emotions['piktas'][0], 'piktas'), (emotions['piktas'][0], 'piktas')])
            if emotions['nustebęs']:
                rodyti_paveikslelius.extend([(emotions['nustebęs'][0], 'nustebęs'), (emotions['nustebęs'][0], 'nustebęs')])
        except Exception as e:
            logger.error(f"Error selecting images: {str(e)}")
            request.session.flush()
            return redirect('emociju_atpazinimas')
        
        # Shuffle while ensuring no consecutive identical emotions
        for _ in range(100):
            random.shuffle(rodyti_paveikslelius)
            valid = True
            for i in range(len(rodyti_paveikslelius) - 1):
                if rodyti_paveikslelius[i][1] == rodyti_paveikslelius[i + 1][1]:
                    valid = False
                    break
            if valid:
                break
        else:
            logger.warning("Could not shuffle without consecutive emotions, using default shuffle")
        
        request.session['rodyti_paveikslelius'] = rodyti_paveikslelius
        request.session['indexas'] = 0
        request.session['game_completed'] = False
        try:
            request.session.modified = True
            request.session.save()
            logger.debug(f"Initialized session: indexas=0, game_completed=False, images={rodyti_paveikslelius}")
        except Exception as e:
            logger.error(f"Session save failed: {str(e)}")
            request.session.flush()
            return redirect('emociju_atpazinimas')

    # Load session data
    try:
        rodyti_paveikslelius = [tuple(el) for el in request.session.get('rodyti_paveikslelius', [])]
        indexas = request.session.get('indexas', 0)
        game_completed = request.session.get('game_completed', False)
    except Exception as e:
        logger.error(f"Error loading session data: {str(e)}")
        request.session.flush()
        return redirect('emociju_atpazinimas')

    # Validate session data
    if not rodyti_paveikslelius or len(rodyti_paveikslelius) != 8 or not all(isinstance(el, tuple) and len(el) == 2 for el in rodyti_paveikslelius):
        logger.warning(f"Invalid session data: rodyti_paveikslelius={rodyti_paveikslelius}, indexas={indexas}, resetting session")
        request.session.flush()
        return redirect('emociju_atpazinimas')

    atsakymas = None

    if request.method == 'POST':
        if 'reset_game' in request.POST:
            request.session.flush()
            logger.debug(f"Session reset triggered")
            return redirect('emociju_atpazinimas')

        if game_completed:
            logger.debug(f"POST ignored: game_completed={game_completed}")
            return render(request, 'emociju_atpazinimas.html', {
                'game_completed': True,
                'progress_percent': 100,
                'completion_message': "Sveikiname! Jūs baigėte emocijų atpažinimo žaidimą!"
            })

        pasirinkta_emocija = request.POST.get('emocija')
        if not pasirinkta_emocija:
            logger.warning("No emotion selected in POST request")
            pasirinktas_paveikslelis = rodyti_paveikslelius[indexas][0]
            progress_percent = int((indexas / len(rodyti_paveikslelius)) * 100)
            return render(request, 'emociju_atpazinimas.html', {
                'paveikslelis': pasirinktas_paveikslelis,
                'atsakymas': "Prašome pasirinkti emociją!",
                'progress_percent': progress_percent,
                'game_completed': game_completed
            })

        tikras_emocija = rodyti_paveikslelius[indexas][1]
        current_image = rodyti_paveikslelius[indexas][0]
        logger.debug(f"Processing answer: indexas={indexas}, pasirinkta_emocija={pasirinkta_emocija}, tikras_emocija={tikras_emocija}, image={current_image}")

        if pasirinkta_emocija == tikras_emocija:
            atsakymas = "teisingai"
        else:
            atsakymas = "neteisingai"
            logger.debug("Incorrect answer")

        if indexas == len(rodyti_paveikslelius) - 1:
            request.session['game_completed'] = True
            try:
                request.session.modified = True
                request.session.save()
                logger.debug(f"Game completed: 8th card answered")
            except Exception as e:
                logger.error(f"Session save failed: {str(e)}")
                request.session.flush()
                return redirect('emociju_atpazinimas')
            return render(request, 'emociju_atpazinimas.html', {
                'paveikslelis': current_image,
                'atsakymas': atsakymas,
                'progress_percent': 100,
                'game_completed': True,
                'completion_message': "Sveikiname! Jūs baigėte emocijų atpažinimo žaidimą!"
            })

        if pasirinkta_emocija == tikras_emocija:
            indexas += 1
            request.session['indexas'] = indexas
            try:
                request.session.modified = True
                request.session.save()
                logger.debug(f"Advanced to indexas={indexas}")
            except Exception as e:
                logger.error(f"Session save failed: {str(e)}")
                request.session.flush()
                return redirect('emociju_atpazinimas')

        progress_percent = int(((indexas + 1) / len(rodyti_paveikslelius)) * 100) if atsakymas == "teisingai" else int((indexas / len(rodyti_paveikslelius)) * 100)
        pasirinktas_paveikslelis = rodyti_paveikslelius[indexas][0]

        return render(request, 'emociju_atpazinimas.html', {
            'paveikslelis': pasirinktas_paveikslelis,
            'atsakymas': atsakymas,
            'progress_percent': progress_percent,
            'game_completed': game_completed
        })

    progress_percent = 100 if game_completed else int((indexas / len(rodyti_paveikslelius)) * 100)
    pasirinktas_paveikslelis = None if game_completed else rodyti_paveikslelius[indexas][0]
    logger.debug(f"Rendering GET: indexas={indexas}, progress_percent={progress_percent}, game_completed={game_completed}")

    context = {
        'paveikslelis': pasirinktas_paveikslelis,
        'atsakymas': atsakymas,
        'progress_percent': progress_percent,
        'game_completed': game_completed
    }
    if game_completed:
        context['completion_message'] = "Sveikiname! Jūs baigėte emocijų atpažinimo žaidimą!"

    return render(request, 'emociju_atpazinimas.html', context)

def pagrindinis(request):
    return render(request, 'pagrindinis.html')

def valgiu_derinimas(request):
    return render(request, 'valgiu_derinimas.html')

def dienos_rezimas(request):
    return render(request, 'dienos_rezimas.html')

def svaros_zaidimas(request):
    return render(request, 'svaros_zaidimas.html')

def veidukas(request):
    return render(request, 'veidukas.html')

def test_template(request):
    templates = [
        'pagrindinis.html',
        'emociju_atpazinimas.html',
        'valgiu_derinimas.html',
        'dienos_rezimas.html',
        'svaros_zaidimas.html',
        'veidukas.html',
    ]
    results = []
    for template in templates:
        try:
            get_template(template)
            results.append(f"Template {template} found!")
        except TemplateDoesNotExist:
            results.append(f"Template {template} not found!")
    return HttpResponse("<br>".join(results))