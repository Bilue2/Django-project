from django.db.models import Avg, Count
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404

from learning_logs.models import Topic, Entry
from learning_logs.forms import TopicForm, EntryForm

import io, base64
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from decimal import Decimal

# Create your views here.
def index(request):
    """The home page for Learning Log."""
    return render(request, "learning_logs/index.html")

@login_required
def topics(request):
    topics = Topic.objects.filter(owner=request.user).order_by('date_added')
    context = {"topics": topics}
    return render(request, "learning_logs/topics.html", context)

@login_required
def topic(request, topic_id):
    """Show a single topic and all its entries."""
    topic = Topic.objects.get(id=topic_id)
     # Make sure the topic belongs to the current user.
    if topic.owner != request.user:
        raise Http404
    entries = topic.entry_set.order_by("-date_added")
    context = {"topic": topic, "entries": entries}
    return render(request, "learning_logs/topic.html", context)

@login_required
def new_topic(request):
    """Add a new topic."""
    if request.method != 'POST':
        # No data submitted; create a blank form.
        form = TopicForm()
    else:
        # POST data submitted; process data.
        form = TopicForm(data=request.POST)
        if form.is_valid():
             new_topic = form.save(commit=False)
             new_topic.owner = request.user
             new_topic.save()
             return redirect('learning_logs:topics')

    context = {'form': form}
    return render(request, 'learning_logs/new_topic.html', context)

@login_required
def new_entry(request, topic_id):
    """Add a new entry for a particular topic."""
    topic = Topic.objects.get(id=topic_id)

    if request.method != 'POST':
        form = EntryForm()
    else:
        form = EntryForm(data=request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.topic = topic
            new_entry.save()
            return redirect('learning_logs:topic', topic_id=topic_id)

    context = {'topic': topic, 'form': form}
    return render(request, 'learning_logs/new_entry.html', context)


@login_required
def edit_entry(request, entry_id):
    """Edit an existing entry."""
    entry = Entry.objects.get(id=entry_id)
    topic = entry.topic
    if topic.owner != request.user:
        raise Http404


    if request.method != 'POST':
        form = EntryForm(instance=entry)
    else:
        form = EntryForm(instance=entry, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect('learning_logs:topic', topic_id=topic.id)

    context = {'entry': entry, 'topic': topic, 'form': form}
    return render(request, 'learning_logs/edit_entry.html', context)




#def get_graph():
    """Convert matplotlib figure to base64 string."""
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    return base64.b64encode(image_png).decode('utf-8')

def get_graph():
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graph = base64.b64encode(image_png).decode('utf-8')
    return graph

@login_required
def stats(request):
    topics = Topic.objects.filter(owner=request.user)
    entries = Entry.objects.filter(topic__in=topics)

    # Helper to safely convert any value to float
    def safe_float(val):
        if val is None:
            return None
        if isinstance(val, (Decimal, int, float)):
            return float(val)
        try:
            return float(val)
        except (ValueError, TypeError):
            return None

    # ------------------ Summary metrics ------------------
    avg_hours = safe_float(entries.aggregate(Avg('hours_spent'))['hours_spent__avg'] or 0)
    avg_exam = safe_float(entries.aggregate(Avg('exam_score'))['exam_score__avg'] or 0)
    total_entries = entries.count()
    type_counts = topics.annotate(total=Count('entry'))

    # ------------------ Hours Studied vs Exam Score ------------------
    hours_exam_chart = ""
    valid_entries = entries.exclude(hours_spent__isnull=True, exam_score__isnull=True)
    plt.figure(figsize=(6,4))
    plt.scatter([safe_float(e.hours_spent) for e in valid_entries],
                [safe_float(e.exam_score) for e in valid_entries], c="#6610f2", alpha=0.6)
    plt.title("Hours Studied vs Exam Score")
    plt.xlabel("Hours Studied")
    plt.ylabel("Exam Score")
    hours_exam_chart = get_graph()
    plt.close()

    # ------------------ School Type Comparison ------------------
    school_type_chart = ""
    school_topic = topics.filter(text='School & Teacher').first()
    if school_topic:
        public_scores = [safe_float(s) for s in Entry.objects.filter(
            topic=school_topic, text__icontains='Public'
        ).exclude(exam_score__isnull=True).values_list('exam_score', flat=True)]
        private_scores = [safe_float(s) for s in Entry.objects.filter(
            topic=school_topic, text__icontains='Private'
        ).exclude(exam_score__isnull=True).values_list('exam_score', flat=True)]
        if public_scores or private_scores:
            plt.figure(figsize=(5,4))
            plt.boxplot([public_scores, private_scores], labels=['Public', 'Private'])
            plt.title("Exam Score Comparison: Public vs Private Schools")
            plt.ylabel("Exam Score")
            school_type_chart = get_graph()
            plt.close()

    # ------------------ Context ------------------
    context = {
        "avg_hours": avg_hours,
        "avg_exam": avg_exam,
        "total_entries": total_entries,
        "type_counts": type_counts,
        "hours_exam_chart": hours_exam_chart,
        "school_type_chart": school_type_chart,
    }

    return render(request, "learning_logs/stats.html", context)




